#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%

import sys

import numpy as np

import matplotlib.pyplot as plt

from filter.source import Source, SourceStream
from filter.basic import HPF, Gain, Memory, Delay, LPF
from filter.wnd import WND, RWND, Blackman, PitchWND
from filter.fft import FFT, IFFT

DATA_10 = np.array([1.0] * 1000 + [0.0] * 1000 + [-1.0]
                   * 1000 + [0.0] * 1000).reshape(-1, 1)
DATA_SIN20 = np.sin(2*np.pi * 20 * np.arange(10000)/44100).reshape(-1, 1)
DATA_1 = np.array([1.0] * 10000).reshape(-1, 1)

DATA_MIX = np.concatenate((DATA_1, DATA_10, DATA_SIN20))
DATA_MIX_SIZE = DATA_MIX.shape[0]


def test_source():

    layer = Source(DATA_MIX, sampling_rate=44100)

    data = layer.get(DATA_MIX_SIZE)

    plt.plot(data[:, 0])


def test_LPF():

    layer = Source(DATA_MIX, sampling_rate=44100)
    layer = LPF(layer, 0.0039, 44100, (0,))

    data = layer.get(DATA_MIX_SIZE)

    plt.plot(data[:, 0])


def test_HPF():

    layer = Source(DATA_MIX, sampling_rate=44100)
    layer = HPF(layer, 0.0039, 44100, (0,))

    data = layer.get(DATA_MIX_SIZE)

    plt.plot(data[:, 0])


# %%
test_source()
test_LPF()
test_HPF()

plt.show()

# %%
