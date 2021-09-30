#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio

from pydub import AudioSegment
import numpy as np
import math

from filter.source import Source
from filter.basic import Gain
from filter.wnd import WND, RWND
from filter.fft import FFT, IFFT
from filter.spectrum import SpectrumShiftA, SpectrumShiftB

from os.path import splitext

from config import *

class Jukebox:
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()

        self.is_down = False

        self.output = None
        self.source = None

        self._is_recording = False
        self._record_data_list = []

        self._sampling_rate = 0
        self._ch = 0

    def __del__(self) -> None:

        if(self.output):
            self.output.stop_stream()
            self.output.close()

        self.audio.terminate()

    def select_music(self, mic: bool = True, musicpath=None):
        if(self.output):
            self.output.close()

        if(mic):
            # 未実装
            pass
        else:
            # 音声データを読み取る
            _, ext = splitext(musicpath)
            audio_data = AudioSegment.from_file(musicpath, format=ext[1:])  # オーディオデータ読み込み
            audio_array_data = audio_data.get_array_of_samples()

            # データが32bit浮動小数型に変換
            # 0.0~1.0の範囲に収めるので2をサンプルサイズで階乗したもので割る
            int_size = 2 ** (audio_data.sample_width * 8)
            audio_array_data = np.array(audio_array_data, dtype=np.float32) / int_size

            # 入力から出力までのフィルタパイプラインを構築
            self._fsource = Source(audio_array_data.reshape((-1,audio_data.channels)), audio_data.frame_rate)

            layer = WND(self._fsource, 1024, 256)
            layer = FFT(layer)
            layer = SpectrumShiftB(layer, 2)
            layer = IFFT(layer)
            layer = RWND(layer, 1024, 256)

            self._fgain = Gain(layer , 1)
            self.source = self._fgain

            def callback(in_data, frame_count, time_info, status):

                # 読み取り
                data = self.source.get(frame_count).astype(np.float32)

                # 録音機能
                if(self._is_recording):
                    np.clip(data, 0.0, 1.0)
                    self._record_data_list += [(data * (2**16 - 1)).astype(np.uint16)]

                return (data, pyaudio.paContinue)

            self._ch = audio_data.channels
            self._sampling_rate = audio_data.frame_rate

            self.output = self.audio.open(format=pyaudio.paFloat32,
                                          channels=self._ch,
                                          rate=self._sampling_rate,
                                          frames_per_buffer=BUFFER_SIZE,
                                          output=True,
                                          stream_callback=callback)

    # フィルタ調整機能

    def set_gain(self, value):
        if self._fgain:
            self._fgain.value = value

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

            record_data = np.ndarray(shape=(recorded_length, self._ch), dtype=np.int16)
            saved_length = 0

            # 保存するデータの長さを計算
            for d in self._record_data_list:
                record_data[saved_length:saved_length + d.shape[0]] = d
                saved_length += d.shape[0]

            ouput_segment = AudioSegment(record_data.tobytes(), sample_width=2, frame_rate=self._sampling_rate, channels=self._ch)

            ouput_segment.export(path)

        self._record_data_list = []
