#!/usr/bin/env python3

import sys
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from matplotlib import axes as ax
from scipy.signal import fir_filter_design as ffd
from scipy.signal import filter_design as ifd
from scipy.signal import *

#################################################################################################
## Command line arguments
##
#if len(sys.argv) != 2:
#    print("usage: {} filename".format(sys.argv[0]))
#    exit(1)

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

data = wav_file.readframes(nframes)
print(len(data))
data = struct.unpack('<{n}h'.format(n=nframes*nchannels), data)
wav_file.close()

if nchannels == 2:
    data = data[0:nframes:2]
    nframes = len(data)
    nchannels = 1
    
#################################################################################################
## Normalize amplitude to -1 to +1 based on bit depth (sampwidth)
##
maxint = 2**(sampwidth*8)
data = [x/maxint for x in data]

#################################################################################################
## Constants
seconds      = nframes / Fsr            # number of seconds in recording
fzero        = 2200.                    # frequency indicating 0
fone         = 1200.                    # frequency indicating 1
bps          = 1200.                    # bits per second
samp_per_bit = int(np.ceil(Fsr/bps))    # samples per bit

#################################################################################################
## Filtering
##
print("Filtering...")

fp = 2300
fs = 10000
gp = 1
gs = 24
wp = fp/Fsr
ws = fs/Fsr

print("fp={} wp={} fs={} ws={}".format(fp, wp, fs, ws))

b, a = iirdesign(wp, ws, gp, gs, analog=False, ftype='cheby1')
data1 = lfilter(b, a, data)

fp = 1100
fs = 10
gs = 24
wp = fp/Fsr
ws = fs/Fsr

b, a = iirdesign(wp, ws, gp, gs, analog=False, ftype='cheby1')
data2 = lfilter(b, a, data1)

#################################################################################################
## Save WAV file
##

def sav_wav(params, d):
    print("Writing wav file...")
    try:
       wav_out = wave.open("out.wav", 'wb')
    except Exception as e:
        print(e)
        exit(2)

    wav_out.setparams(params)
    ## todo: Convert amplitude back to 16-bit
    dout = [int(word) for word in d.tolist()]
    frames = struct.pack('<{n}h'.format(n=nframes), *dout)
    wav_out.writeframes(frames)
    wav_out.close()

#sav_wav([nchannels, sampwidth, Fsr, nframes, comptype, compname], data2)

#################################################################################################
## Plot data
##
print("Plotting...")
nrows = 2
ncols = 2

fig, ax = plt.subplots(num=None, figsize=(20, 12), dpi=80, facecolor='w', edgecolor='k')
plt.subplot(nrows,ncols,1)
plt.title('Original Waveform')
plt.plot(data)

plt.subplot(nrows,ncols,2)
plt.title('Filtered Waveform')
plt.plot(data2)

maxf = 5000 ## maximum freq to plot on FFT

plt.subplot(nrows,ncols,3)
plt.title('Original FFT')
N = int(len(data)/2)
Y = np.fft.fft(data)
freq = np.fft.fftfreq(len(data), 1/Fsr)
plt.plot(freq[0:maxf/2], np.abs(Y[0:maxf/2]))

plt.subplot(nrows,ncols,4)
plt.title('Filtered FFT')
N = int(len(data2)/2)
Y = np.fft.fft(data2)
freq = np.fft.fftfreq(len(data2), 1/Fsr)
plt.plot(freq[0:maxf/2], np.abs(Y[0:maxf/2]))

plt.show()   



print("Done.")
