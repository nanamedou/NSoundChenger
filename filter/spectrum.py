#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# スペクトラム領域での演算を行うフィルタ
# FFTとIFFTの間で使う

import numpy as np

from filter.base import FilterBase, FilterRoot, InheritCh

# 音程変更フィルタ
# スペクトラムをずらす
# d > 0 で高周波数域にずらす
# d < 0 で低周波数域にずらす

class SpectrumShift(InheritCh):
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

        if(offs > 0):
            data_fft = np.concatenate((
                np.zeros(shape=(offs, self._ch)),
                data_fft[0:size//2 - offs],
                data_fft[size//2 + offs:size],
                np.zeros(shape=(offs, self._ch))))


        elif(offs < 0):
            offs = -offs
            data_fft = np.concatenate((
                data_fft[offs:size//2],
                np.zeros(shape=(offs, self._ch)),
                np.zeros(shape=(offs, self._ch)),
                data_fft[size//2:size-offs]))

        return data_fft

    @property
    def value(self):
        return self._d
    
    @value.setter
    def value(self, d):
        self._d = int(d)

# 音程変更フィルタ
# スペクトラムを低周波数域にずらす

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

# 音程変更フィルタ
# スペクトラムを高周波数域にずらす

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

        self._generate_matrix()


    # 音のピッチを変更するための行列作成。
    # 行列サイズはsize*size
    def _generate_matrix(self):
        size = self._size
        scale = self._scale

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
        self._mat = modspec # 音のピッチを変更するための行列

        dw = f - w
        dw = np.tile(dw, (self._ch, 1))
        dw = dw.T
        self._dw = dw       # 変換後の音と元の音の角速度の差

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


    @property
    def value(self):
        return self._scale
    
    @value.setter
    def value(self, scale: float):
        self._scale = float(scale)
        self._generate_matrix()

class SupressSmallNoize(InheritCh):

    def __init__(self, source: FilterBase, db_dffs: float = 20):
        super().__init__(source)
        self._db = db_dffs
        self._threshold_mod = 1 / np.power(10, db_dffs / 20)

    def get(self, size):

        data = self._source.get(size).copy()

        for c in range(data.shape[1]):
            sqdata = np.square(data[:,c])
            m = np.max(sqdata)
            threshold = m * np.square(self._threshold_mod)
            np.putmask(data[:,c], np.square(sqdata) < threshold, 0j)

        return data


    @property
    def value(self):
        return self._db
    
    @value.setter
    def value(self, db_dffs: float):
        self._db = float(db_dffs)
        self._threshold_mod = 1 / np.power(10, db_dffs / 20)

