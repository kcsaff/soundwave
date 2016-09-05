import bisect
from collections import namedtuple


KeyPointer = namedtuple('KeyPointer', ('age', 'life', 'item'))


KeyFrame = namedtuple('KeyFrame', ('time', 'pointers'))


class Timeline(object):
    def __init__(self):
        self.keyframes = list()

    def _find(self, time):
        index = bisect.bisect_left(self.keyframes, (time,))

