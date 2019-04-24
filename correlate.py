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
samp_per_bit = int(np.ceil(Fsr/bps))   # samples per bit


#print("Resampling...")

## Resample
#data = resample(x=data, num=int(seconds * Fsr) )
#nframes = len(data)

print("Fsr={} samp_per_bit={} nframes={}".format(Fsr, samp_per_bit, nframes))

## filter design arguements
Fpass = 1200.    # passband edge
Fstop = 2200.    # stopband edge
Wp = Fpass/Fsr   # pass normalized frequency
Ws = Fstop/Fsr   # stop normalized frequency

#print("Filtering...")
## Create a filter
taps = 16
br = ffd.remez(taps, [0, Wp, Ws, .5], [1,0], maxiter=10000)
br = ffd.firwin2(taps, [0, Wp, Ws, 1], [0, 1, 1, 0])
br = ffd.firwin(taps, cutoff=[Wp, Ws], window='blackmanharris', pass_zero=False)

# Once you have the coefficients from a filter design, (b for FIR b and a for IIR) you can use
# a couple different functions to perform the filtering: lfilter, convolve, filtfilt. Typically
# all these functions operate similar: y = filtfilt(b,a,x)
# If you have a FIR filter simply set a=1, x is the input signal, b is the FIR coefficients.
data = lfilter(br, 1, data)

## Correlation

chunk_size = 1024  # number of samples to capture and then evaluate

template_0 = [0 for i in range(chunk_size)]
template_1 = [0 for i in range(chunk_size)]

K = 2*np.pi/Fsr

for s in range(samp_per_bit):
#for s in range(chunk_size):
    template_0.append(-np.cos(s*K*fzero))
    template_1.append(-np.cos(s*K*fone))
    
#plt.subplot(1,1,1)
#plt.plot(range(len(template_0)), template_0, 'r-x', template_1, 'b-x')
#plt.show()
    
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
b, a = butter(5, bps*2/Fsr, btype='low')
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
plt.plot(range(len(correlate_0)), correlate_0, 'r-', correlate_1, 'b-')
plt.subplot(4,1,3)
plt.plot(both)
plt.subplot(4,1,4)
plt.plot(digi)
plt.show()   

exit()

# IQ multiplication
dec_0_i = []
dec_0_q = []
dec_1_i = []
dec_1_q = []
d_0_iq = []
d_1_iq = []
d_iq = []

mean_0_i = []
mean_0_q = []
offset_0 = []
mean_1_i = []
mean_1_q = []
offset_1 = []
offset = []

print("IQ Decoding...")

for s in range(nframes):
    phi = s * 2 * np.pi / Fsr
    dec_0_i.append( np.cos(phi*fzero)*data[s] )
    dec_0_q.append( np.sin(phi*fzero)*data[s] )
    dec_1_i.append( np.cos(phi*fone)*data[s] )
    dec_1_q.append( np.sin(phi*fone)*data[s] )

print("Filtering IQ...")
## Low pass filter these waveforms
b, a = butter(5, 30/Fsr, btype='low')
zi = lfilter_zi(b, a)
i_0, _ = lfilter(b, a, dec_0_i, zi=zi*dec_0_i[0])
q_0, _ = lfilter(b, a, dec_0_q, zi=zi*dec_0_q[0])
i_1, _ = lfilter(b, a, dec_1_q, zi=zi*dec_1_q[0])
q_1, _ = lfilter(b, a, dec_1_q, zi=zi*dec_1_q[0])

print("Computing mean...")

## Find mean across bit period; basically running average
## Can use zero crossings to detect 0->1, 1->0 transitions
for s in range(int(nframes)):
    a = s
    b = s+samp_per_bit-1
    #i_0 = np.mean(dec_0_i[a:b])
    #q_0 = np.mean(dec_0_q[a:b])
    #i_1 = np.mean(dec_1_i[a:b])
    #q_1 = np.mean(dec_1_q[a:b])

    mag_0 = np.sqrt(i_0[s]**2 + q_0[s]**2)
    mag_1 = np.sqrt(i_1[s]**2 + q_1[s]**2)

    #mean_0_i.append(i_0)
    #mean_0_q.append(q_0)
    offset_0.append(mag_0)
    #mean_1_i.append(i_1)
    #mean_1_q.append(q_1)
    offset_1.append(mag_1)
    offset.append(mag_1 - mag_0)

nsubs = 4

ax.grid(which='major')

plt.subplot(nsubs,1,1)
plt.plot(data)
plt.title("Time domain audio wave")

#data_fft = np.fft.fft(np.array(data))
#frequencies = np.abs(data_fft)
#plt.subplot(nsubs,1,2)
#plt.plot(frequencies)
#plt.title("Frequencies found")
#plt.xlim(0,20000)

#plt.subplot(nsubs,1,2)
#plt.title("IQ Decode")
#plt.plot(range(nframes), dec_0_i, 'r', dec_0_q, 'g', dec_1_i, 'c', dec_1_q, 'b')

plt.subplot(nsubs,1,2)
plt.title("Mean(I,Q) and Magnitude: 0")
plt.plot(range(nframes), offset_0, 'r', i_0, 'b--', q_0, 'c--')

plt.subplot(nsubs,1,3)
plt.title("Mean and Offset, 1")
plt.plot(range(nframes), offset_1, 'r', i_1, 'b--', q_1, 'c--')

plt.subplot(nsubs,1,4)
plt.title("0 and 1 combined")
plt.plot(offset)


plt.show()
