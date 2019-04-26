
# APRS Notes

## Goal: process APRS packets in embedded system

## Questions, notes, todo, etc.

 * IIR filter best for embedded?
 * verify: phase response screwing with tones
 * verify: phase response for various band pass filters

## Decoding Steps
 * Demodulate AFSK to get 1's and 0's
 * Decode from non-return to zero inverted (NRZI) line encoding including unstuffing bits
 * Decode X.25 frame
 * Decode APRS packet


APRS Layers (http://n1vg.net/packet/)

| OSI Layer | Description | Implementation |
|-----------|-------------|----------------|
| Network   | Packets     | APRS           |
| Data Link | Frames      | AX.25          |
| Physical  | Bits        | AFSK, NRZ      |


## APRS Information Field (http://www.aprs.org/doc/APRS101.PDF)

The AX.25 Destination Address field can contain 6 different types of APRS
information:

 * A generic APRS address.
 * A generic APRS address with a symbol.
 * An APRS software version number.
 * Mic-E encoded data.
 * A Maidenhead Grid Locator (obsolete).
 * An Alternate Net (ALTNET) address.

In all of these cases, the Destination Address SSID may specify a generic APRS digipeater path.

## FCS bit-at-a-time algorithm

 * FCS is a two-byte checksum added to the end of every frame.
 * FCS is generated using the CRC-CCITT polynomial, and is sent low-byte first.
 * Start with the 16-bit FCS set to 0xffff.
 * For each data bit sent:
   * Shift the FCS value right one bit.
   * If the bit that was shifted off (formerly bit 1) was not equal to the bit being sent,
     * Exclusive-OR the FCS value with 0x8408.
 * After the last data bit, take the ones complement (inverse) of the FCS value and send it low-byte first.


## X.25

 * AX.25 protocol defines the packet format.
 * Based on the High Level Data Link Control protocol, or HDLC.
 * Frames start and end with the binary sequence 01111110
 * This sequence is not bit stuffed, so this is the only time you'll see a run of six 1s. 
 * Frame Check Sequence (FCS) checksum. 
 * packet structure: 
   * Flag 1
   * Destination Address 7
   * Source address 7
   * Digipeater addresses: 56
   * Control field 1
   * ID 1
   * Information Field: 256
   * FCS 1
   * Flag 1

Bit Stuffing the NRZI bitstream
 * Any run of five 1s has a 0 inserted after the fifth 1

NRZI
 * 0 is encoded as a change in tone, and 
 * 1 is encoded as no change in tone.

AFSK
 * Audio Frequency-Shift Keying
 * Two tones: 0 == 2200Hz, 1 == 1200Hz 
 * tones must be continuous phase
