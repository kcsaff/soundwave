import random


try:
    long = __builtins__.long
except:
    long = int


class Dither(object):
    def __init__(self, count=1):
        self.count = count

    def random(self, maxdither):
        return sum(
            random.uniform(maxdither)
            for _ in range(self.count)
        ) / self.count

    def __call__(self, sample, maxdither):
        return long(sample + self.random(maxdither))


dither1 = Dither(1)
dither2 = Dither(2)
