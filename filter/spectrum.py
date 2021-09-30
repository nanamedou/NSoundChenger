#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# スペクトラム領域での演算を行うフィルタ
# FFTとIFFTの間で使う

import numpy as np

from filter.base import FilterBase, FilterRoot, InheritCh

# 音程変更フィルタ
# fft


class SpectrumShiftA(InheritCh):

    def __init__(self, source: FilterBase, d: int):
        super().__init__(source)
        self._d = d

    def get(self, size):

        # 低音化フィルター
        offs = self._d

        start_point = self._source.sample_start_point
        data_fft = self._source.get(size).copy()

        dt = 2.0j * np.math.pi * start_point * offs / size
        dr = np.exp(dt)
        data_fft *= dr

        data_fft = np.concatenate((
            data_fft[offs:size//2],
            np.zeros(shape=(offs, self._ch)),
            np.zeros(shape=(offs, self._ch)),
            data_fft[size//2:size-offs]))

        return data_fft

class SpectrumShiftB(InheritCh):

    def __init__(self, source: FilterBase, d: int):
        super().__init__(source)
        self._d = d

    def get(self, size):

        # 高音化フィルター
        offs = self._d

        start_point = self._source.sample_start_point
        data_fft = self._source.get(size).copy()

        dt = -2.0j * np.math.pi * start_point * offs / size
        dr = np.exp(dt)
        data_fft *= dr

        data_fft = np.concatenate((
            np.zeros(shape=(offs, self._ch)),
            data_fft[0:size//2 - offs],
            data_fft[size//2 + offs:size],
            np.zeros(shape=(offs, self._ch))))

        return data_fft

# 音のピッチを変更する
# 変更はスケールで変える。
#
class SpectrumPitch(InheritCh):


    def __init__(self, source: FilterBase, size: int, scale: float):
        super().__init__(source)
        self._size = size
        self._scale = scale

        # 音のピッチを変更するための行列作成。
        # 行列サイズはsize*size

        # x[f, t] = cos(2 * pi * f * t / T) をDTFTした結果X[f, w]を周波数成分Y[w]にかけると
        # ゲインと角度がY[w]で周波数がfのスペクトルが得られる
        # なので以下の式で音程を変更できる
        # / X[f0, w0] X[f1, w0] ・・・ X[fT-1, w0]      \        /  Y[w0] \ 
        # | X[f0, w1] X[f1, w1] ・・・ X[fT-1, w1]       |    *  |  Y[w1]  |
        # |                     ・・・                   |       |    ・   |
        # \ X[f0, wT-1] X[f1, wT-1] ・・・ X[fT-1, wT-1]  /       \ Y[wT-1]/ 
        # これの左の行列を求める

        w = np.fft.fftfreq(size)
        f = np.power(2, scale / 12) * w
        f2pi = (2.0 * np.pi) * f
        f2pi = f2pi.reshape(1, size)
        t = np.arange(size)
        t = t.reshape(size, 1)
        # コサイン波[t, f]を作成
        wav = np.exp(t @ f2pi * 1j) / size
        # コサイン波のDTFT[w, f]を作成
        modspec = np.fft.fft(wav, n=size, axis=0)
        self._mat = modspec
        dw = f - w
        dw = np.tile(dw, (self._ch, 1))
        dw = dw.T
        self._dw = dw

    def get(self, size):

        start_point = self._source.sample_start_point
        data = self._source.get(size)

        if size != self._size:
            return data

        dt = 2.0j * np.pi * start_point * self._dw
        dr = np.exp(dt)
        data = data * dr
        data = self._mat @ data

        return data