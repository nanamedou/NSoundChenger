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
        self._cur = -delay
        self._buffer = np.zeros((delay, self._ch))

    # dataは bitデータ * チャンネルデータ
    # 出力は bitデータ * チャンネルデータ
    def get(self, size):

        data = np.array(self._buffer[0:size])

        self._buffer[:-size] = self._buffer[size:]
        self._buffer[-size:] = self._source.get(size)
        self._cur += size

        return data

    @property
    def sample_start_point(self):
        return self._cur

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

    def __init__(self, source: FilterBase, gain: float):
        super().__init__(source)
        if(gain < 0):
            print('nanamesst->filter->Gain: gain must positive!!')
            gain = 0.0
        self._value = float(gain)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = float(value)

    # dataは bitデータ * チャンネルデータ
    # 出力は bitデータ * チャンネルデータ

    def get(self, size):

        data = self._source.get(size) * self._value

        return data

# 音程変更フィルタ
# 音をn倍速再生して音程を変える
# Wndで挟んで使うとテンポを変えずにピッチだけ変えられる


class Pitch(InheritCh):

    def __init__(self, source: FilterBase, scale: float):
        super().__init__(source)
        self.value = float(scale)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = float(value)
        self._speed = np.exp2(self._value / 12)

    def get(self, size):


        speed = self._speed

        # 初期位置の補正値の計算
        st = speed
        st -= 1
        st *= self._source.sample_start_point % size

        # サンプル位置の計算
        point = np.arange(size) * speed
        point += st

        # インデックスと重みの計算
        f, i = np.modf(point)
        f = f.reshape(-1,1)
        i = i.astype(np.int32)
        i %= size

        # 出力の計算
        data = self._source.get(size)

        data = np.concatenate((data, [data[0]]))
        out = data[i] * (1 - f) + data[i + 1] * f

        return out

# メモリフィルタ
# 直前に通過した内容を読み取ることができる


class Memory(InheritCh):

    def __init__(self, source: FilterBase):
        super().__init__(source)
        self._data = np.zeros((0, 1))

    def get(self, size):

        data = self._source.get(size)
        self._data = data.copy()

        return data

    @property
    def data(self):
        return self._data
