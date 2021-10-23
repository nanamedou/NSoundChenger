#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading as th

import numpy as np

from filter.base import FilterBase, InheritCh


class WND(InheritCh):
    """矩形窓関数フィルタ

    wndmoveだけずらしたwndsizeのデータを返す
    例) source[0:wndsize] & source[wndmove :wndmove + wndsize] & source[wndmove * 2 :wndmove * 2 + wndsize] & ...

    """

    def __init__(self, source: FilterBase, wndsize: int, wndmove: int):
        super().__init__(source)
        self._buffer = np.zeros(shape=(wndsize, source._ch))
        self._wndsize = wndsize
        self._wndmove = wndmove
        self._cur = -wndsize + wndmove      # 書き出すデータのソースにおける頭の位置

    def get(self, size):

        # wndmoveだけずらしたwndsizeのデータを返す

        if(size != self._wndsize):
            print('nsc->filter->WND: Requested size is not equal wndsize!!')
            return np.zeros(shape=(self._ch, self._wndsize))

        data = self._source.get(self._wndmove)
        data = np.concatenate((self._buffer[self._wndmove:], data))
        self._buffer = data
        self._cur += self._wndmove

        return data

    @property
    def sample_start_point(self) -> int:
        return self._cur


class RWND(InheritCh):
    """窓結合関数

    窓関数で分割されたデータを結合する

    """

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


class Hamming(InheritCh):
    """ハミング関数フィルタ
    """

    def __init__(self, source: FilterBase, size: int):
        super().__init__(source)
        self._filter = np.blackman(size)

    def get(self, size):
        data = self._source.get(size).copy()

        data *= self._filter.reshape(-1, 1)

        return data


class Hanning(InheritCh):
    """ハニング関数フィルタ
    """

    def __init__(self, source: FilterBase, size: int):
        super().__init__(source)
        self._filter = np.hanning(size)

    def get(self, size):
        data = self._source.get(size).copy()

        data *= self._filter.reshape(-1, 1)

        return data


class Blackman(InheritCh):
    """ブラックマン関数フィルタ
    """

    def __init__(self, source: FilterBase, size: int):
        super().__init__(source)
        self._filter = np.blackman(size)

    def get(self, size):
        data = self._source.get(size).copy()

        data *= self._filter.reshape(-1, 1)

        return data


class Padding(InheritCh):
    """中央よせ0パディング

    in[4],out[8]の時以下のように変換する
    1111
    00111100

    2の倍数の大きさである必要がある
    """

    def __init__(self, source: FilterBase, size_in: int, size_out: int):
        super().__init__(source)
        self._buffer = np.zeros(shape=(size_out, self._ch))
        self._size_in = size_in
        self._size_out = size_out

    def get(self, size):

        self._buffer.fill(0)

        mid = self._size_out // 2
        half_in = self._size_in // 2

        self._buffer[mid - half_in:mid +
                     half_in] = self._source.get(self._size_in)

        return self._buffer


class Suppress(InheritCh):
    """中央よせ0サプレス

    in[8],out[4]の時以下のように変換する
    00111100
    1111

    2の倍数の大きさである必要がある
    """

    def __init__(self, source: FilterBase, size_in: int, size_out: int):
        super().__init__(source)
        self._size_in = size_in
        self._size_out = size_out

    def get(self, size):

        mid = self._size_in // 2
        half_out = self._size_out // 2

        return self._source.get(self._size_in)[mid - half_out:mid + half_out]


class PitchWND(InheritCh):
    """ピッチ変更窓関数

    矩形窓関数フィルタにピッチ変更処理を組み合わせた
    ピッチを変更方法は、
    まず、出力の2**(scale/12) * 2倍のデータをサンプリングする。
    そこからちょうど良い、出力の2**(scale/12)倍のデータを選ぶ。
    出力のサイズまで縮める。
    以上。

    """

    def __init__(self, source: FilterBase, wndsize_out: int, wndmove: int, scale: float):
        super().__init__(source)

        self.lock = th.Lock()

        self._wndsize_out = wndsize_out
        self._wndsize_in = wndsize_out
        self._wndmove = wndmove
        self._buffer = np.zeros(
            shape=(wndsize_out, self._ch), dtype=np.float32)
        self.value = float(scale)
        self._cur = -self._wndsize_out + wndmove      # 書き出すデータのソースにおける頭の位置

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.lock.acquire()

        # ピッチの変更量を更新
        self._value = float(value)
        self._speed = np.exp2(self._value / 12)

        # 出力する時間の長さに対する、サンプル期間を測定
        sample_duration = self._wndsize_out * self._speed
        self.sample_duration = sample_duration

        # サンプル期間から必要なバッファの期間とサイズを計測
        required_duration = sample_duration * 2
        self.buffer_duration = required_duration
        required_samples = int(required_duration) + 2

        if(required_samples > self._buffer.shape[0]):
            add_buf_size = required_samples - self._buffer.shape[0]
            self._buffer.resize((required_samples, self._ch))
            self._buffer[-add_buf_size:] = self._source.get(add_buf_size)

        self.lock.release()

    def get(self, size):

        self.lock.acquire()

        # wndmoveだけずらしたwndsizeのデータを返す
        if(size != self._wndsize_out):
            print('nsc->filter->PitchWND: Requested size is not equal wndsize!!')
            return np.zeros(shape=(self._ch, self._wndsize_out))

        data = self._source.get(self._wndmove)
        data = np.concatenate((self._buffer[self._wndmove:], data))
        self._buffer[:] = data
        self._cur += self._wndmove

        # 波の移動速度の取得
        speed = self._speed
        in_dur = self.sample_duration
        out_size = self._wndsize_out
        buf_dur = self.buffer_duration

        # 初期位置の補正値の計算
        # ((speed - 1) * 再生位置) % サンプル期間
        st = speed.copy()
        st -= 1
        st *= np.remainder(self._cur, out_size)
        st %= in_dur

        # サンプル位置の計算
        point = np.arange(out_size) * speed
        point += st
        point = np.fmod(point, buf_dur)

        # インデックスと重みの計算
        f, i = np.modf(point)
        f = f.reshape(-1, 1)
        i = i.astype(np.int32)

        # 出力の計算
        out = data[i] * (1 - f) + data[i + 1] * f

        self.lock.release()

        return out

    @property
    def sample_start_point(self) -> int:
        return self._cur
