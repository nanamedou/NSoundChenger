#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%

import sys

import numpy as np

import matplotlib.pyplot as plt

from filter.source import Source, SourceStream
from filter.basic import HPF, Gain, Memory, Delay, LPF
from filter.spectrum import SupressStationaryNoize
from filter.wnd import WND, RWND, Blackman, PitchWND
from filter.fft import FFT, IFFT


DATA_1 = np.array([1.0] * 10000).reshape(-1, 1)

DATA_10 = np.array([1.0] * 1000 + [0.0] * 1000 + [-1.0]
                   * 1000 + [0.0] * 1000).reshape(-1, 1)

DATA_SIN20 = np.sin(2*np.pi * 20 * np.arange(10000)/44100).reshape(-1, 1)
DATA_SIN20_SIZE = DATA_SIN20.shape[0]

DATA_SIN100 = np.sin(2*np.pi * 100 * np.arange(10000)/44100).reshape(-1, 1)
DATA_SIN100_SIZE = DATA_SIN100.shape[0]

DATA_MIX = np.concatenate((DATA_1, DATA_10, DATA_SIN20, DATA_SIN100))
DATA_MIX_SIZE = DATA_MIX.shape[0]

# %%
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

def test_SupressStationaryNoize():

    wndsize = 2048
    wndmove = 128
    sampling_rate = 44100

    plt.plot(DATA_SIN100)

    layer = Source(DATA_SIN100, sampling_rate)
    layer = WND(layer, wndsize, wndmove)
    #layer = Blackman(layer, wndsize)
    layer = FFT(layer)
    
    layer = SupressStationaryNoize(layer, wndsize, wndmove / sampling_rate, 0.1, 0.3)
    layer = IFFT(layer)
    layer = RWND(layer, wndsize, wndmove)

    data = layer.get(DATA_SIN100_SIZE*2)

    plt.plot(data[:, 0])

# %%
test_SupressStationaryNoize()

plt.show()

# %%

# %%
