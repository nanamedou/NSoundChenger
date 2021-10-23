#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio

from pydub import AudioSegment
import numpy as np
import math

from filter.source import Source, SourceStream
from filter.basic import Gain, Memory, Pitch, Delay
from filter.wnd import WND, RWND, Hamming, Padding, Suppress, PitchWND
from filter.fft import FFT, IFFT
from filter.spectrum import SupressSmallNoize

from os.path import splitext

class Jukebox:
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()

        self.is_enable = True

        self.output = None

        self._is_recording = False
        self._record_data_list = []

        self._sampling_rate = 0
        self._ch = 0

    def __del__(self) -> None:

        self.disable()

    def enable(self) -> None:
        if(self.is_enable == False):
            self.is_enable = True

            self.output = None

            self._is_recording = False
            self._record_data_list = []

            self._sampling_rate = 0
            self._ch = 0

    def disable(self) -> None:

        if(self.is_enable):
            self.is_enable = False
            if(self.output):
                self.output.stop_stream()
                self.output.close()

            self.audio.terminate()
    
    def make_pipeline(self, source):
            layer = source
            self._fsource = layer

            layer = Delay(layer, 44100)

            layer = PitchWND(layer, 2048, 128, 0)
            self._fspshift = layer
            layer = Hamming(layer, 2048)
            layer = RWND(layer, 2048, 128)

            
            layer = WND(layer, 1024, 128)

            layer = FFT(layer)
            self._ffft = layer

            layer = Memory(layer)
            self._ffftspectrum = layer

            layer = IFFT(layer)

            layer = RWND(layer, 1024, 128)

            layer = Gain(layer, 1)
            self._fgain = layer

            layer = Memory(layer)
            self._fmemout = layer

            self.output_layer = layer

            def callback(in_data, frame_count, time_info, status):

                # 読み取り
                data = self.output_layer.get(frame_count).astype(np.float32)

                # 録音機能
                if(self._is_recording):
                    data = np.clip(data, 0.0, 1.0)
                    self._record_data_list += [(data *
                                                (2**16 - 1)).astype(np.uint16)]

                return (data, pyaudio.paContinue)

            return callback 


    def select_music(self, mic: bool = True, musicpath=None):
        if(self.output):
            self.output.close()

        if(mic):

            self._ch = 1
            self._sampling_rate = 44100

            self.input = self.audio.open(format=pyaudio.paFloat32,
                                          channels=self._ch,
                                          rate=self._sampling_rate,
                                          frames_per_buffer=1024,
                                          input=True,
                                          input_device_index=0)

            sound_source = SourceStream(self.input,self._ch,self._sampling_rate)

        else:
            # 音声データを読み取る
            _, ext = splitext(musicpath)
            audio_data = AudioSegment.from_file(
                musicpath, format=ext[1:])  # オーディオデータ読み込み
            audio_array_data = audio_data.get_array_of_samples()

            # データが32bit浮動小数型に変換
            # 0.0~1.0の範囲に収めるので2をサンプルサイズで階乗したもので割る
            int_size = 2 ** (audio_data.sample_width * 8)
            audio_array_data = np.array(
                audio_array_data, dtype=np.float32) / int_size

            sound_source = Source(audio_array_data.reshape(
                (-1, audio_data.channels)), audio_data.frame_rate)

            self._ch = audio_data.channels
            self._sampling_rate = audio_data.frame_rate

        # 入力から出力までのフィルタパイプラインを構築
        callback = self.make_pipeline(sound_source)

        self.output = self.audio.open(format=pyaudio.paFloat32,
                                        channels=self._ch,
                                        rate=self._sampling_rate,
                                        frames_per_buffer=1024,
                                        output=True,
                                        stream_callback=callback)

    # フィルタ調整機能

    def set_gain(self, value):
        if self._fgain:
            self._fgain.value = value

    def set_spshift(self, value):
        if self._fspshift:
            self._fspshift.value = value

    def set_supress_small_noize(self, value):
        if value:
            self._ffftspectrum.set_source(self._fsupress_small_noize)
        else:
            self._ffftspectrum.set_source(self._ffft)

    # 再生機能

    def play(self):
        if(self.output):
            self.output.start_stream()

    def stop(self):
        if(self.output):
            self.output.stop_stream()

    # 録音機能

    @property
    def is_recording(self):
        return self._is_recording

    def record_start(self):
        self._is_recording = True

    def record_stop(self):
        self._is_recording = False

    def record_save(self, path):

        if(len(self._record_data_list) > 0):
            record_data = self._record_data_list[0]

            # 保存するデータのサンプル時間数を計算
            recorded_length = 0
            for d in self._record_data_list:
                recorded_length += d.shape[0]

            record_data = np.ndarray(
                shape=(recorded_length, self._ch), dtype=np.int16)
            saved_length = 0

            # 保存するデータの長さを計算
            for d in self._record_data_list:
                record_data[saved_length:saved_length + d.shape[0]] = d
                saved_length += d.shape[0]

            ouput_segment = AudioSegment(record_data.tobytes(
            ), sample_width=2, frame_rate=self._sampling_rate, channels=self._ch)

            ouput_segment.export(path)

        self._record_data_list = []

    # 分析機能

    def analyzer_spectrum(self):
        return self._ffftspectrum.data[:, 0]

    def analyzer_oscillo(self):
        return self._fmemout.data[:, 0]
