#!/bin/sh

## Extracts wav files from bin and cue file sharing same basename
##
## usage: $0 basename

if [ "$#" -lt 2 ]; then
  echo "usage: $0 basename"
  exit 1
fi

name="$1"

if [ -f $name.bin ] && [ -f $name.cue ]; then
  bchunk -w ${name}.bin ${name}.cue track
else
  echo "no such file: $name"
  exit 2
fi
