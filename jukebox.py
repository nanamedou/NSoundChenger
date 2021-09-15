#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from numpy.core.fromnumeric import shape
import pyaudio

from pydub import AudioSegment
import numpy as np
import math

from os.path import splitext

from config import *


class Jukebox:
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()

        self.is_down = False
        self.cursor = 0

        self.output = None

        pass

    def __del__(self) -> None:

        if(self.output):
            self.output.stop_stream()
            self.output.close()

        self.audio.terminate()

        pass

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

            self.cursor = 0
            self.lastoutput = np.zeros(audio_data.channels)

            def callback(in_data, frame_count, time_info, status):

                # 読み取る時間計算
                readsize = frame_count * audio_data.channels

                # 読み取り
                raw_data = audio_array_data[self.cursor:(
                    self.cursor + readsize)].copy()


                # 読み取り完了判定
                if(len(raw_data) < readsize):
                    endflag = pyaudio.paComplete
                else:
                    endflag = pyaudio.paContinue

                if(raw_data.size == 0):
                    return ([], pyaudio.paComplete)

                # データを読み取りやすく
                data = raw_data.astype(dtype=np.float32)
                data.resize(frame_count * audio_data.channels)
                data = data.reshape((frame_count, audio_data.channels))

                def voice_change(data_in, sample_rate, samples, channels):
                    data_out = np.zeros_like(data_in)

                    # 高音化フィルター
                    for ch in range(channels):
                        data_fft = np.fft.fft(data_in[:, ch])
                        offs = 1000
                        
                        data_fft = np.concatenate((
                            np.zeros_like(data_fft[offs:samples//2]),
                            data_fft[0:offs],
                            data_fft[samples-offs:samples],
                            np.zeros_like(data_fft[samples//2:samples-offs])))

                        start_rad = float(self.cursor) / float(offs)
                        
                        dt = 2 * math.pi * start_rad
                        dr = np.complex(np.cos(dt), np.sin(dt))
                        data_fft[0:samples // 2] *= dr
                        data_fft[samples // 2: samples] *= dr.conjugate()

                        data_out[:, ch] = np.fft.ifft(data_fft).real

                    print(data_out.size)

                    return data_out

                def lcf(data_in, RC, dt, power0):
                    data_out = np.zeros_like(data_in)

                    # 高音化フィルター
                    for channel in range(audio_data.channels):
                        data_ic_view = data_in[:, channel]
                        data_oc_view = data_out[:, channel]
                        oldsig = power0[channel]
                        for i in range(len(data_ic_view)):
                            newsig = oldsig + (1.0 / RC) * \
                                (data_ic_view[i] - oldsig) * dt
                            data_oc_view[i] = newsig
                            oldsig = newsig

                    return data_out

                # data = lcf(data, 300 * (10 ** (-6)), 1 /
                #           audio_data.frame_rate, self.lastoutput)
                #self.lastoutput = data[-1, :]

                data = voice_change(data, audio_data.channels,
                                    frame_count, audio_data.channels)

                # 読み取り位置変更
                self.cursor += readsize

                return (data.astype(dtype=raw_data.dtype), endflag)

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
