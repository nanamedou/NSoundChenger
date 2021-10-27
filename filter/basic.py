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



class LPF(InheritCh):
    """ローパスフィルタ

    CRローパスフィルタを再現する線形フィルタ
    """

    def __init__(self, source, rc, sample_rate, initial):
        super().__init__(source)
        self.mems = np.zeros(self._ch)  # 積分器メモリ
        self.memd = np.zeros(self._ch)  # フィードバックメモリ
        self.rc = rc                    # rc
        self.sample_rate = sample_rate  # サンプル周波数
        self.dt = 1.0 / sample_rate     # 1サンプル当たりの時間
        self.rrc = 1.0 / self.rc        # rcの逆数

    def get(self, size):
        data = self._source.get(size)
        buf = np.zeros_like(data)

        for x, y in zip(data, np.arange(buf.shape[0])):
            x2 = x - self.memd              # フィードバックで差分を取得
            x3 = x2 * self.dt * self.rrc    # 時間とrcで変化量決定
            self.mems += x3                 # 積分
            buf[y] = self.mems              # 出力する
            self.memd = self.mems           # フィードバックメモリに格納

        return buf

        
class HPF(InheritCh):
    """ハイパスフィルタ

    CRハイパスフィルタを再現する線形フィルタ
    """


    def __init__(self, source, rc, sample_rate, initial):
        super().__init__(source)
        self.mems = np.zeros(self._ch)  # 積分器メモリ
        self.memd = np.zeros(self._ch)  # フィードバックメモリ
        self.rc = rc                    # rc
        self.sample_rate = sample_rate  # サンプル周波数
        self.dt = 1.0 / sample_rate     # 1サンプル当たりの時間
        self.rrc = 1.0 / self.rc        # rcの逆数

    def get(self, size):
        data = self._source.get(size)
        buf = np.zeros_like(data)

        for x, y in zip(data, np.arange(buf.shape[0])):
            x2 = x - self.memd              # フィードバックで差分を取得
            buf[y] = x2                     # 出力する
            x3 = x2 * self.dt * self.rrc    # 時間とrcで変化
            self.mems += x3                 # 積分
            self.memd = self.mems           # フィードバックメモリに格納

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
