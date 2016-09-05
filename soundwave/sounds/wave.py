from __future__ import absolute_import
import array
from contextlib import closing
import itertools
from itertools import zip_longest
import wave
import struct

from .channel import ChannelData


_FORMATS = [
    (1, 'B'),
    (2, 'h'),
    (4, 'l'),
    (8, 'q'),
]


_FORMAT_LENS = {
    'b': 1,
    'B': 1,
    'h': 2,
    'H': 2,
    'i': 2,
    'I': 2,
    'l': 4,
    'L': 4,
    'q': 8,
    'Q': 8,
}


def read_channels(filename):
    with closing(wave.open(filename, 'rb')) as f:
        samplerate = f.getframerate()
        bytewidth = f.getsampwidth()
        signed = (bytewidth > 1)
        shiftbits = 0
        for bw, typecode in _FORMATS:
            if bw == bytewidth:
                break
            elif bw > bytewidth:
                shiftbits = 8 * (bw - bytewidth)
                break
        else:
            raise NotImplementedError('Cannot read WAVE file with sample width {}'.format(bytewidth))

        channel_count = f.getnchannels()
        channels = [
            ChannelData(samplerate, typecode)
            for _ in range(channel_count)
        ]

        samplecount = f.getnframes()
        blocksize = 1024
        for _ in range(0, samplecount, blocksize):
            frame = f.readframes(blocksize)
            for i in range(blocksize * channel_count):
                bytesample = frame[bytewidth*i:bytewidth*(i+1)]
                sample = int.from_bytes(bytesample, 'little', signed=signed) << shiftbits
                channels[i % channel_count].append(sample)

        return channels


def write_channels(filename, *channels):
    if not all(c.samplerate == channels[0].samplerate for c in channels):
        raise ValueError('samplerate must be consistent')
    if not all(c.typecode == channels[0].typecode for c in channels):
        raise ValueError('typecode must be consistent')
    with closing(wave.open(filename, 'wb')) as f:
        f.setnchannels(len(channels))
        f.setsampwidth(channels[0].itemsize)
        f.setframerate(channels[0].samplerate)
        format = '<' + channels[0].typecode * len(channels)
        longest = max(len(c) for c in channels)
        f.setnframes(longest)
        for frame in zip_longest(*channels, fillvalue=0):
            f.writeframesraw(struct.pack(format, *frame))



