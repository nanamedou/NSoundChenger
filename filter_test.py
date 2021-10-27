#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import matplotlib.pyplot as plt


from filter.source import Source, SourceStream
from filter.basic import Gain, Memory, Delay
from filter.wnd import WND, RWND, Blackman, PitchWND
from filter.fft import FFT, IFFT

def test_source():

    layer = Source(np.ones((1024,1)),sampling_rate=44100)

    data = layer.get(2048)

    plt.plot(data[:,0])

    plt.show()


test_source()