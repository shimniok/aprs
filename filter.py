#!/usr/bin/env python3

import sys
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
from matplotlib import axes as ax
from scipy.signal import fir_filter_design as ffd
from scipy.signal import filter_design as ifd
from scipy.signal import *

#################################################################################################
## Command line arguments
##
if len(sys.argv) != 2:
    print("usage: {} filename".format(sys.argv[0]))
    exit(1)

#################################################################################################
## Read wav file
##
print("Reading file...")

try:
    wav_file=wave.open(sys.argv[1], 'r')
except Exception as e:
    print(e)
    exit(2)

(nchannels, sampwidth, Fsr, nframes, comptype, compname) = wav_file.getparams()

print("{}: {} channels, {} bit, {} Hz, {} frames".format(sys.argv[1], nchannels, sampwidth * 8, Fsr, nframes))

if nchannels != 1:
    print("can only run on mono wav files, sorry!")
    exit(3)

data = wav_file.readframes(nframes)
data = struct.unpack('<{n}h'.format(n=nframes), data)
wav_file.close()

seconds      = nframes / Fsr            # number of seconds in recording
fzero        = 2200.                    # frequency indicating 0
fone         = 1200.                    # frequency indicating 1
bps          = 1200.                    # bits per second
samp_per_bit = int(np.ceil(Fsr/bps))    # samples per bit

#################################################################################################
## Filtering
##
print("Filtering...")

fp = 2400 
fs = 4400 
gp = 5
gs = 60

## Low pass
wp = fp/Fsr
ws = fs/Fsr
b, a = iirdesign(wp, ws, gpass=2., gstop=10., analog=False, ftype='butter')
data2 = lfilter(b, a, data)

#################################################################################################
## Save WAV file
##

#try:
#    wav_file=wave.open("out.wav", 'wb')
#except Exception as e:
#    print(e)
#    exit(2)

#wav_file.setparams([nchannels, sampwidth, Fsr, len(data2), comptype, compname])
#frames = struct.pack('<{n}h'.format(n=nframes), np.array(data2))
#wav_file.writeframes(frames)
#wav_file.close()

#################################################################################################
## Plot data
##
plt.subplot(2,1,1)
plt.plot(data)
plt.subplot(2,1,2)
plt.plot(data2)
plt.show()   


