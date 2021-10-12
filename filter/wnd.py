#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import write
import numpy as np
from numpy.lib.function_base import hamming

from filter.base import FilterBase, InheritCh

# 窓関数
# 矩形窓関数フィルタ
# wndmoveだけずらしたwndsizeのデータを返す
# 例) source[0:wndsize] & source[wndmove :wndmove + wndsize] & source[wndmove * 2 :wndmove * 2 + wndsize] & ...


class WND(InheritCh):

    def __init__(self, source: FilterBase, wndsize: int, wndmove: int):
        super().__init__(source)
        self._buffer = np.zeros(shape=(wndsize, source._ch))
        self._wndsize = wndsize
        self._wndmove = wndmove
        self._cur = -wndsize + wndmove      # 書き出すデータのソースにおける頭の位置

    def get(self, size):

        # wndmoveだけずらしたwndsizeのデータを返す

        if(size != self._wndsize):
            print('nanamesst->filter->WND: Requested size is not equal wndmove!!')
            return np.zeros(shape=(self._ch, self._wndsize))

        data = self._source.get(self._wndmove)
        data = np.concatenate((self._buffer[self._wndmove:], data))
        self._buffer = data
        self._cur += self._wndmove

        return data

    @property
    def sample_start_point(self) -> int:
        return self._cur


class Hamming(InheritCh):

    def __init__(self, source: FilterBase, size: int):
        super().__init__(source)
        self._hamming = np.hamming(size)

    def get(self, size):
        data = self._source.get(size).copy()

        for c in range(self._ch):
            data[:, c] *= self._hamming

        return data


class IHamming(InheritCh):

    def __init__(self, source: FilterBase, size: int):
        super().__init__(source)
        self._ihamming = 1 / np.hamming(size)

    def get(self, size):
        data = self._source.get(size).copy()

        for c in range(self._ch):
            data[:, c] *= self._ihamming

        return data


# 窓結合関数
# 窓関数で分割されたデータを結合する
class RWND(InheritCh):

    def __init__(self, source: FilterBase, wndsize: int, wndmove: int):
        super().__init__(source)
        self._buffer = np.zeros(shape=(wndsize, source._ch))  # 結合済みデータ保存バッファ
        self._buffer2 = np.zeros(
            shape=(wndsize, source._ch))  # 読み取りデータ一時保存バッファ
        self._wndsize = wndsize
        self._wndmove = wndmove
        self._datamod = wndmove / wndsize  # 窓移動量/窓サイズ　ソースから得たデータの重さに使う
        self._bufcur = wndsize
        self._cur = 0      # 書き出したデータサイズ

    def get(self, size):

        # リターン用のメモリを確保し0で初期化する。書き込み用カーソル位置は0
        res = np.zeros(shape=(size, self._ch))
        rescur = 0

        # 要求データ量のsizeが0になるまでデータの読出しを繰り返す
        while size > 0:

            # バッファ読み取りカーソル位置が読み取り範囲[wndmove:]のときずっと
            # ソースからデータを読み取りwndmoveだけ時間を進めたバッファと合成
            # カーソル位置も前にずらす
            while self._bufcur >= self._wndmove:

                self._bufcur -= self._wndmove
                self._buffer2[:] = self._source.get(
                    self._wndsize)  # ソースからデータを読み取り
                self._buffer2[:] *= self._datamod                   # 合成前の処理
                # 結合前データと合成
                self._buffer2[:-self._wndmove] += self._buffer[self._wndmove:]
                d = self._buffer                                    # バッファのスワップ
                self._buffer = self._buffer2
                self._buffer2 = d

            # バッファの[0:wndmove]の区間だけ読出しをする。この区間は窓関数で分割した値が掛け合わされている。
            # 読み取りカーソル位置+読み取り要求サイズが[0:wndmove]の区間内であれば、そのままバッファから読み取りカーソル等を変更数する。
            if self._bufcur + size <= self._wndmove:
                res[rescur:rescur+size] = self._buffer[self._bufcur:self._bufcur+size]
                self._bufcur += size
                rescur += size
                size = 0

            # 読み取りカーソル位置+読み取り要求サイズが[0:wndmove]の区間外であれば、いったん、wndmoveまでのバッファを読み取りカーソルを変更する。
            else:
                writesize = self._wndmove - self._bufcur
                res[rescur:rescur +
                    writesize] = self._buffer[self._bufcur:self._bufcur + writesize]
                self._bufcur = self._wndmove
                rescur += writesize
                size -= writesize

        return res
