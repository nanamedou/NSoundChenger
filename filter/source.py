#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from numpy.core.fromnumeric import shape

import pyaudio

from filter.base import FilterBase, FilterRoot

from pydub import AudioSegment

from os.path import splitext


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
            res = np.concatenate(
                (res, np.zeros(shape=(size-readsize, self._ch))))

        return res

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @property
    def sample_start_point(self) -> int:
        return self._cur


class SourceStream(FilterRoot):

    def __init__(self, data, ch, sampling_rate):
        super().__init__(ch)
        self._data = data
        self._cur = 0
        self._sampling_rate = sampling_rate

    def get(self, size):

        res = np.zeros(shape=(size, self._ch))

        read_size = 0

        while(read_size < size):
            d = np.frombuffer(self._data.read((size - read_size) * self._ch, exception_on_overflow = False), dtype=np.float32)
            res[read_size:read_size+d.shape[0]] = d.reshape(-1,self._ch)
            read_size += d.shape[0]

        self._cur += size

        return res

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @property
    def sample_start_point(self) -> int:
        return self._cur
