#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from filter.base import FilterBase, InheritCh


# 遅延フィルタ
class Delay(InheritCh):

    def __init__(self, source: FilterBase, delay: int):
        super().__init__(source)
        if(delay < 0):
            print('nanamesst->filter->Delay: delay must positive!!')
            delay = 0
        self._cur = delay
        self._delay = delay

    # dataは bitデータ * チャンネルデータ
    # 出力は bitデータ * チャンネルデータ
    def get(self, size):

        data = np.zeros(shape=(size,self._ch))

        # デェレイ中の時データは読み取らない
        if(self._cur > size):
            read_size = 0
            self._cur -=  size
        # デェレイが終わってたらサイズ分読み取る
        else:
            read_size = size - self._cur
            self._cur = 0

        data[size-read_size:size] = self._source.get(read_size)

        return data

    @property
    def sample_start_point(self):
        return self._source.sample_start_point - self._delay

# ローパスフィルタ
# rcローパスフィルタを再現する線形フィルタ
class LPF(FilterBase):

    def __init__(self, source, ch, rc, sample_rate, initial, channels):
        super().__init__(source, ch)
        self.initial = initial
        self.rc = rc
        self.sample_rate = sample_rate
        self.dt = 1.0 / sample_rate
        self.channels = channels

    # dataは bitデータ * チャンネルデータ
    # 出力は bitデータ * チャンネルデータ
    def get(self, size):
        data = self.source.get(size)
        buf = np.zeros_like(data)
        for channel in range(self.channels):
            data_ic_view = data[:, channel]
            data_oc_view = buf[:, channel]
            oldsig = self.initial[channel]
            rc = self.rc
            dt = self.dt
            for i in range(len(data_ic_view)):
                newsig = oldsig + (1.0 / rc) * (data_ic_view[i] - oldsig) * dt
                data_oc_view[i] = newsig
                oldsig = newsig
            self.initial[channel] = oldsig

        return buf

# ゲインフィルタ
class Gain(InheritCh):
    
    def __init__(self, source: FilterBase, gain: int):
        super().__init__(source)
        if(gain < 0):
            print('nanamesst->filter->Gain: gain must positive!!')
            delay = 0
        self._gain = gain

    # dataは bitデータ * チャンネルデータ
    # 出力は bitデータ * チャンネルデータ
    def get(self, size):

        data = self._source.get(size) * self._gain

        return data
