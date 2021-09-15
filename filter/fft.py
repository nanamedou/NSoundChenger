#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from filter.base import FilterBase, InheritCh

# FFTフィルタークラス
# ソースを(size, ch)だけ読み取ってFFTしたもの(size, ch)を返す
class FFT(InheritCh):

    def __init__(self, source:FilterBase):
        super().__init__(source)

    def get(self, size):

        data_in = self._source.get(size)
        data_out = np.fft.fft(data_in, n=size, axis=0)

        return data_out

# IFFTフィルタークラス
# ソースを(size, ch)だけ読み取ってIFFTしたもの(size, ch)を返す
class IFFT(InheritCh):

    def __init__(self, source:FilterBase):
        super().__init__(source)

    def get(self, size):

        data_in = self._source.get(size)
        data_out = np.fft.ifft(data_in, n=size, axis=0)

        return data_out.real