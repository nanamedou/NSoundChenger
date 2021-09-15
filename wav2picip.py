# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython


# %%
get_ipython().system('set PATH=%PATH%;I:\ffmpeg')


from pydub import AudioSegment
from pydub.utils import make_chunks

import sys
from os.path import splitext

import numpy as np
import math

import matplotlib.pyplot as plt


# %%
INPUT_FILENAME = "./sounds/sin.wav"

audio_data = AudioSegment.from_file(INPUT_FILENAME, format=splitext(INPUT_FILENAME)[1][1:])

data = np.array(audio_data.get_array_of_samples())
data = data.astype(np.float64)
data = data.reshape(-1,audio_data.channels)


# %%
# プロットができるかの確認
fig, ax = plt.subplots(2, 1)
ax[0].plot([0, 1],[0, 1], color="red")
ax[1].plot([0, 1],[0, 1], color="blue")
plt.show()


# %%
def plotgraph(ax, data, point):
    for ch in range(audio_data.channels):
        ax[audio_data.channels * point + ch].plot(data[:,ch], linewidth=0.3)

def plotgraph2(ax, x, data, point):
    for ch in range(audio_data.channels):
        ax[audio_data.channels * point + ch].scatter(x, data[:,ch],s=2)

def voice_change(data_in, sample_rate, samples, channels, start_point):
    data_out = np.zeros_like(data_in)

    # 高音化フィルター
    for ch in range(channels):
        data_fft = np.fft.fft(data_in[:, ch], samples)
        offs = 4

        dt = 2.0 * math.pi * start_point * offs / samples
        dr = np.complex(np.cos(dt), np.sin(dt))
        data_fft *= dr
        
        data_fft = np.concatenate((
            data_fft[offs:samples//2],
            np.zeros(offs),
            np.zeros(offs),
            data_fft[samples//2:samples-offs]))
            
        # data_fft[0] += 2 * sum0

        data_out[:, ch] = np.fft.ifft(data_fft, samples).real

    return data_out

def lcf(data_in, RC, dt, power0):
    data_out = np.zeros_like(data_in)

    # 高音化フィルター
    for channel in range(audio_data.channels):
        data_ic_view = data_in[:,channel]
        data_oc_view = data_out[:,channel]
        oldsig = power0[channel] 
        for i in range(len(data_ic_view)):
            newsig = oldsig + (1.0 / RC) * (data_ic_view[i]- oldsig) * dt
            data_oc_view[i] = newsig
            oldsig = newsig

    return data_out

rc = 200 * (10 ** (-6))
dt = 1 / audio_data.frame_rate


# %%

from filter.source import Source
from filter.wnd import WND,RWND,Hamming,IHamming
from filter.fft import FFT,IFFT
from filter.spectrum import SpectrumPitch, SpectrumShiftA,SpectrumShiftB

GRAPH_V = 2
g_id = 0

test_size = 4096
wnd_size = 1024
wnd_move = 128

fig, ax = plt.subplots(GRAPH_V, audio_data.channels)

plotgraph(ax, data[:test_size], g_id)
g_id += 1

a = Source(data[0:test_size], audio_data.frame_rate)
a = WND(a, wnd_size, wnd_move)
#a = Hamming(a, wnd_size)
a = FFT(a)
#a = SpectrumShiftA(a, 4)
a = SpectrumPitch(a, wnd_size, 0)
#a = SpectrumShiftB(a, 4)
#a = SpectrumPitch(a, wnd_size, 12)
a = IFFT(a)
#a = IHamming(a, wnd_size)
a = RWND(a, wnd_size, wnd_move)

result = a.get(test_size)
plotgraph(ax, result, g_id)
g_id += 1



# %%
from filter.source import Source
from filter.wnd import WND,RWND,Hamming
from filter.fft import FFT,IFFT
from filter.spectrum import SpectrumShiftA, SpectrumShiftB,SpectrumPitch
from filter.basic import Delay

plt.figure(figsize=(8, 8))
GRAPH_V = 5
g_id = 0

test_size = 128 * 4
test_sp = test_size * 2
test_scale = 8

fig, ax = plt.subplots(GRAPH_V, audio_data.channels)

d = np.zeros(shape=(test_size,1), dtype=np.complex128)
d[4] = 1-1j
d[-4] = 1+ 1j
d[6] = 1 + 1j
d[-6] = 1 - 1j
d[30] = 1
d[30] = 1
plotgraph(ax, d.real, g_id)
plotgraph(ax, d.imag, g_id)
g_id += 1

a = Source(d , audio_data.frame_rate)
a = IFFT(a)
a = RWND(a, test_size, test_size)
a = Delay(a, 128 * 3)
a = FFT(a)
a = SpectrumPitch(a, test_size, test_scale)
a = IFFT(a)
res = a.get(test_size)
plotgraph(ax, res.real, g_id)
plotgraph(ax, res.imag, g_id)
g_id += 1

a = Source(d , audio_data.frame_rate)
a = IFFT(a)
a = RWND(a, test_size, test_size)
a = Delay(a, 128 * 2)
a = FFT(a)
a = SpectrumPitch(a, test_size, test_scale)
a = IFFT(a)
res = a.get(test_size)
plotgraph(ax, res.real, g_id)
plotgraph(ax, res.imag, g_id)
g_id += 1


a = Source(d , audio_data.frame_rate)
a = IFFT(a)
a = RWND(a, test_size, test_size)
a = Delay(a, 128 * 1)
a = FFT(a)
a = SpectrumPitch(a, test_size, test_scale)
a = IFFT(a)
res = a.get(test_size)
plotgraph(ax, res.real, g_id)
plotgraph(ax, res.imag, g_id)
g_id += 1

a = Source(d , audio_data.frame_rate)
a = IFFT(a)
a = RWND(a, test_size, test_size)
a = Delay(a, 128 * 0)
a = FFT(a)
a = SpectrumPitch(a, test_size, test_scale)
a = IFFT(a)
res = a.get(test_size)
plotgraph(ax, res.real, g_id)
plotgraph(ax, res.imag, g_id)
g_id += 1

plt.savefig("test.svg")

# %%

# %%
