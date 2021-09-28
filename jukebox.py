#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio

from pydub import AudioSegment
import numpy as np
import math

from filter.source import Source

from os.path import splitext

from config import *


class Jukebox:
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()

        self.is_down = False
        self.cursor = 0

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
            _, ext = splitext(musicpath)
            audio_data = AudioSegment.from_file(musicpath, format=ext[1:])
            audio_array_data = np.array(audio_data.get_array_of_samples())

            self.source = Source(audio_array_data.reshape((-1,audio_data.channels)), audio_data.frame_rate)

            self.cursor = 0
            self.lastoutput = np.zeros(audio_data.channels)

            def callback(in_data, frame_count, time_info, status):

                # 読み取り
                data = self.source.get(frame_count)

                return (data, pyaudio.paContinue)

            self.output = self.audio.open(format=self.audio.get_format_from_width(audio_data.sample_width),
                                          channels=audio_data.channels,
                                          rate=audio_data.frame_rate,
                                          frames_per_buffer=BUFFER_SIZE,
                                          output=True,
                                          stream_callback=callback)

    def play(self):
        if(self.output):
            self.output.start_stream()

    def stop(self):
        if(self.output):
            self.output.stop_stream()

    def save(self):
        # 未実装
        pass
