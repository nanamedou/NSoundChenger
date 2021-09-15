##?

from pydub import AudioSegment
from pydub.utils import make_chunks

import sys
from os.path import splitext

import numpy as np
import math

import matplotlib.pyplot as plt

INPUT_FILENAME = sys.argv[1]

audio_data = AudioSegment.from_file(INPUT_FILENAME, format=splitext(INPUT_FILENAME)[1][1:])

data = np.array(audio_data.get_array_of_samples())
data = data.astype(np.float64)
data = data.reshape(-1,audio_data.channels)

fig = plt.figure()

def plotgraph(data, point):
    for ch in range(audio_data.channels):
        ax = fig.add_subplot(GRAPH_V, audio_data.channels,audio_data.channels * point + ch + 1)
        ax.plot(data[:,ch])
        
def plotgraph2(x, data, point):
    for ch in range(audio_data.channels):
        ax = fig.add_subplot(GRAPH_V, audio_data.channels,audio_data.channels * point + ch + 1)
        ax.scatter(x, data[:,ch],s=2)

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

GRAPH_V = 2
def test1():
    global GRAPH_V, data
    GRAPH_V = 2
    g_id = 0

    plotgraph(data, g_id)
    g_id += 1

    wnd_size = 1024
    wnd_move = 256

    if(len(data) % wnd_size != 0):
        new_size = (len(data) // wnd_size + 1) * wnd_size
        data = data.copy()
        data.resize((new_size, data.shape[1]))

    buf = np.zeros((len(data) + wnd_size,  data.shape[1]))

    for i in range(-wnd_size, len(data), wnd_move):
        s = max(0, i)
        t = min(i + wnd_size, len(data))
        data_in = data[s:t]
        data_in = np.pad(data_in, ((max(-i, 0), max(0, i + wnd_size - len(data))), (0,0)), mode='constant')

        new_sound = voice_change(data_in, audio_data.frame_rate, 1024, audio_data.channels, i)
        
        buf[s:t] += new_sound[s-i:t-i]

    data = buf / (wnd_size / wnd_move)

    plotgraph(data, g_id)
    g_id += 1

def test2():
    global GRAPH_V, data
    GRAPH_V = 3
    g_id = 0

    plotgraph(data[0:1024], g_id)
    g_id += 1

    sp = np.fft.fft(data[0:1024], axis = 0)
    fq = np.fft.fftfreq(1024, 1/1024)

    plotgraph(sp.real, g_id)
    g_id += 1

    plotgraph(sp.imag, g_id)
    g_id += 1

def test2():
    global GRAPH_V, data
    GRAPH_V = 3
    g_id = 0

    plotgraph(data[0:1024], g_id)
    g_id += 1

    a = np.fft.fft(data[0:1024])
    b = np.fft.ifft(a)

    plotgraph(a, g_id)
    g_id += 1

    plotgraph(b, g_id)
    g_id += 1



test1()

plt.show()

#audio_data.export()