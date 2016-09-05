import array
from fractions import gcd
import math
import six
from .interpolate import linear as linear_interpolate
from .dither import dither2


try:
    long = __builtins__.long
except:
    long = int


class ChannelData(object):
    def __init__(self, samplerate, typecode, data=(), arraytype=None):
        self.samplerate = samplerate
        typecode = typecode or data.typecode
        self.data = (arraytype or array.array)(typecode, data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    @property
    def typecode(self):
        return self.data.typecode

    @property
    def itemsize(self):
        return self.data.itemsize

    def append(self, sample):
        self.data.append(sample)

    def extend(self, samples):
        self.data.extend(samples)

    def convert(self, samplerate=None, typecode=None, interpolate=None, dither=None, force=True):
        samplerate = samplerate or self.samplerate
        typecode = typecode or self.typecode
        if not force and samplerate == self.samplerate and typecode == self.typecode:
            return self

        if self.samplerate == samplerate:
            resample = self.data
            force_digitize = False
        else:
            interpolate = interpolate or linear_interpolate
            newlen = int(math.ceil(len(self) * samplerate / self.samplerate))
            if isinstance(self.samplerate, six.integer_types) and \
                    isinstance(samplerate, six.integer_types):
                thegcd = gcd(self.samplerate, samplerate)
                numerator = self.samplerate // thegcd
                denominator = samplerate // thegcd
            else:
                numerator = self.samplerate
                denominator = samplerate
            resample = (
                interpolate(self.data, i * numerator, denominator)
                for i in range(newlen)
            )
            force_digitize = True

        return self.__class__(
            convert_typecode(
                resample, self.typecode, typecode, dither,
                force_digitize=force_digitize
            ), samplerate, typecode
        )


_TYPES = {
    'b': (8, -128, 127),
    'B': (8, 0, 255),
    'h': (16, -32768, 32767),
    'H': (16, 0, 65535),
    'i': (16, -32768, 32767),
    'I': (16, 0, 65535),
    'l': (32, -2147483648, 2147483647),
    'L': (32, 0, 4294967295),
    'q': (64, -9223372036854775808, 9223372036854775807),
    'Q': (64, 0, 18446744073709551615),
}


def convert_typecode(fromtype, totype, data, dither=None, force_digitize=True):
    if fromtype in 'fd' or totype in 'fd':
        raise NotImplementedError('We don\'t deal in floats yet sorry :(')
    elif fromtype in 'uc' or totype in 'uc':
        raise NotImplementedError('We don\'t deal in string characters sorry :(')
    else:
        frombits, fromlow, _ = _TYPES[fromtype]
        tobits, tolow, _ = _TYPES[totype]
        dither = dither or dither2
        if frombits > tobits:
            lostbits = frombits - tobits
            maxdither = 1 << lostbits
            return (
                (dither(sample - fromlow, maxdither) >> lostbits) + tolow
                for sample in data
            )
        elif tobits > frombits:
            newbits = tobits - frombits
            maxdither = 1 << newbits
            halfdither = maxdither >> 1
            return (
                dither(((sample - fromlow) << newbits) - halfdither, maxdither)
                for sample in data
            )
        elif force_digitize or fromlow != tolow:
            lowdiff = tolow - fromlow
            return (long(sample + lowdiff) for sample in data)
        else:
            return data


class ChannelMixer(object):
    def __init__(self, samplerate, typecode, interpolate=None, dither=None):
        self.samplerate = samplerate
        self.typecode = typecode
        self.interpolate = interpolate or linear_interpolate
        self.dither = dither or dither2


