#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from filter.base import FilterBase, FilterRoot

# FFTフィルタークラス
# ソースを(ch, size)だけ読み取ってFFTしたもの(ch, size)を返す


class Source(FilterRoot):

    def __init__(self, data, sampling_rate):
        super().__init__(data.shape[1])
        self._data = data.copy()
        self._cur = 0
        self._sampling_rate = sampling_rate

    def get(self, size):

        res = self._data[self._cur: self._cur + size]
        self._cur += size

        readsize = res.shape[0]

        if(readsize < size):
            res = np.concatenate((res, np.zeros(shape=(size-readsize, self._ch))))

        return res

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @property
    def sample_start_point(self) -> int:
        return self._cur

