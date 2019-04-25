#!/usr/bin/env python3

import sys
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
from matplotlib import axes as ax
from scipy.signal import fir_filter_design as ffd
from scipy.signal import filter_design as ifd
from scipy.signal import resample, lfilter, butter, lfilter_zi, correlate, fftconvolve

if len(sys.argv) != 2:
    print("usage: {} filename".format(sys.argv[0]))
    exit(1)

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

print("Reading file...")

## Read wav file
data = wav_file.readframes(nframes)
data = struct.unpack('<{n}h'.format(n=nframes), data)
wav_file.close()
#print(data)

seconds      = nframes / Fsr            # number of seconds in recording
fzero        = 2200.                    # frequency indicating 0
fone         = 1200.                    # frequency indicating 1
bps          = 1200.                    # bits per second
Fsr          = 19200.                   # new sample rate
samp_per_bit = int(np.ceil(Fsr/bps))    # samples per bit

## Band Pass
print("Filtering...")

wp = [1100./Fsr, 2300./Fsr]

b, a = iirdesign(wp, ws=[0.1, 0.5], gpass=5, gstop=-40, analog=False, ftype='ellip', output='ba')

data = lfilter(b, a, data)

## Resample
print("Resampling...")
data = resample(x=data, num=int(seconds * Fsr) )
nframes = len(data)

print("Fsr={} samp_per_bit={} nframes={}".format(Fsr, samp_per_bit, nframes))

## Correlation
print("Correlating...")
chunk_size = 256  # number of samples to capture and then evaluate

emphasize_0 = 1
emphasize_1 = 1

K = 2*np.pi/Fsr
template_0 = [0 for i in range(chunk_size)]
template_1 = [0 for i in range(chunk_size)]
for s in range(samp_per_bit):
    template_0.append(emphasize_0 * -np.cos(s*K*fzero))
    template_1.append(emphasize_1 * -np.cos(s*K*fone))
    
# correlate each chunk
correlate_0 = []
correlate_1 = []
c = 0
while c < len(data):
    chunk = data[c:c+chunk_size-1]
    c0 = correlate(chunk, template_0, 'full').tolist()
    c1 = correlate(chunk, template_1, 'full').tolist()
    for i in range(chunk_size):
        c0[i] *= -c0[i]
        c1[i] *= c1[i]
    
    #plt.subplot(2,1,1)
    #plt.plot(chunk)
    #plt.subplot(2,1,2)
    #plt.plot(range(len(c0)), c0, 'r-', c1, 'b-')
    #plt.show()
    correlate_0 += c0[0:chunk_size]
    correlate_1 += c1[0:chunk_size]
    c += chunk_size

# low pass filter
b, a = butter(5, 2200/Fsr, btype='low')
zi = lfilter_zi(b, a)
filt_corr_0, _ = lfilter(b, a, correlate_0, zi=zi*correlate_0[0])
filt_corr_1, _ = lfilter(b, a, correlate_1, zi=zi*correlate_1[0])

digi = []
both = []
for i in range(len(filt_corr_0)):
    both.append(filt_corr_0[i] + filt_corr_1[i])
    if both[i] > 0:
        digi.append(1)
    else:
        digi.append(0)

plt.subplot(4,1,1)
plt.plot(data)
plt.subplot(4,1,2)
plt.plot(range(len(correlate_0)), filt_corr_0, 'r-', filt_corr_1, 'b-')
plt.subplot(4,1,3)
plt.plot(both)
plt.subplot(4,1,4)
plt.plot(digi)
plt.show()   

