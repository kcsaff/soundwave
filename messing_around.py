"""PyAudio Example: Play a wave file (callback version)"""

import pyaudio
import wave
import math
import time
import random
import struct
import sys

from array import array

SECOND = 48000
AUTO_VOLUME_INTERVAL = 4800.0
from collections import deque

p = pyaudio.PyAudio()

class generator(object):
    def __init__(self, bps, freqs, components, volume=(1 << 10)):
        self._size = 1
        while self._size < SECOND:
            self._size <<= 1
        self.values = array("f", [volume * (random.random() - 0.5) for _ in range(self._size)])
        print(self.values[:16])
        self._size -= 1
        print(self._size)
        self.index = 0
        self.bps_delay = int(SECOND * 1.0 / bps)
        self.delays = [SECOND * 1.0 / F for F in freqs]
        self.components = self.fix_components(components)
        self.volume = volume
        self.auto_volume = volume
        self.running_sum = 0
        self.running_sum_squares = volume * volume
        began = time.time()
        self.data = self.make_data(1024 * 1024)
        print(self.next(), time.time() - began)
        self.i = 0

    def fix_components(self, components):
        s = sum(C[1] for C in components)
        components = [(C[0], C[1] - s * 1.0 / len(components)) for C in components]
        s = sum(abs(C[1]) for C in components)
        components = [(C[0], C[1] / s) for C in components]
        return components

    def make_data(self, frame_count):
        res = array("h", [int(self.next()) for _ in range(frame_count)])
        return res.tobytes()

    def get(self, index):
        delay = self.delays[int(self.index / self.bps_delay + random.random()) % len(self.delays)]
        return self.values[int(self.index + index * delay + random.random()) & self._size] + random.choice((-1, 0, 0, 1))

    def next(self):
        x = sum(self.get(C[0]) * C[1] for C in self.components)
        x -= self.running_sum
        x *= self.volume / math.sqrt(self.running_sum_squares)
        self.index += 1
        self.values[self.index & self._size] = x

        self.running_sum += x / AUTO_VOLUME_INTERVAL
        self.running_sum_squares = (self.running_sum_squares * AUTO_VOLUME_INTERVAL + x*x) / (AUTO_VOLUME_INTERVAL + 1)
        return x

    def callback(self, in_data, frame_count, time_info, status):
        end = self.i + frame_count * 2
        if end > len(self.data):
            return (self.make_data(frame_count), pyaudio.paContinue)
        ret = (self.data[self.i:end], pyaudio.paContinue)
        self.i = end
        return ret

G = generator(3, [441], [
    (0, 0.25),
    (0.50, -0.25),
    (1, 0.125),
    (1.5, -0.125),
    (2, 0.0625),
    (2.5, -0.0625),
    (3, 0.0625),
    (3.5, -0.0625),
])

# G = generator(440, [
#     lambda F: F(0) * 0.5,
#     lambda F: F(0.50) * -0.5,
# ])

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=SECOND,
                output=True,
                stream_callback=G.callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()