#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio

from pydub import AudioSegment
import numpy as np
import math

from filter.source import Source
from filter.basic import Gain

from os.path import splitext

from config import *

class Jukebox:
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()

        self.is_down = False

        self.output = None
        self.source = None

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
            self._fgain = Gain(self._fsource , 1)
            self.source = self._fgain

            def callback(in_data, frame_count, time_info, status):

                # 読み取り
                data = self.source.get(frame_count).astype(np.float32)

                return (data, pyaudio.paContinue)

            self.output = self.audio.open(format=pyaudio.paFloat32,
                                          channels=audio_data.channels,
                                          rate=audio_data.frame_rate,
                                          frames_per_buffer=BUFFER_SIZE,
                                          output=True,
                                          stream_callback=callback)

    def set_gain(self, value):
        if self._fgain:
            self._fgain.value = value

    def play(self):
        if(self.output):
            self.output.start_stream()

    def stop(self):
        if(self.output):
            self.output.stop_stream()

    def save(self):
        # 未実装
        pass
