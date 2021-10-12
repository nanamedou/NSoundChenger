#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


class FilterBase:

    def __init__(self, source, ch: int):
        self._source = source
        self._ch = ch

    # 出力は bitデータ * チャンネルデータ
    def get(self, size):
        return self._source.get(size)

    def set_source(self, source, i=0):
        self._source = source

    @property
    def sampling_rate(self):
        return self._source.sampling_rate

    @property
    def sample_start_point(self):
        return self._source.sample_start_point

class FilterRoot(FilterBase):

    def __init__(self, ch):
        super().__init__(None, ch)

    # 出力は bitデータ * チャンネルデータ
    def get(self, size):
        return self._source.get(size)

    @property
    def sampling_rate(self) -> int:
        return -1

    @property
    def sample_start_point(self) -> int:
        return -1


class InheritCh(FilterBase):

    def __init__(self, source):
        super().__init__(source, source._ch)
