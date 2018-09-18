# -*- coding: utf-8 -*-

from collections import deque


class hdict(dict):
    # Fixme: specify first
    """ hdict (history dict) is a kind of immutable dict that preserves its history.
        history is stored in a deque
    """
    def __init__(self, *args, **kwargs):
        """ if histo is a deque, extend the currunt history, eventually erasing future states
            if histi is None or an int, create a new instance
        """
        histo = kwargs.pop('histo', None)
        dict.__init__(self, *args, **kwargs)
        if isinstance(histo, deque):
            self.histo = histo
            self.pos = kwargs.pop('pos')
            if self.pos < len(histo):
                # Fixme truncate end of deque
                histo[self.pos] = self
            else:
                histo.append(self)
            self.pos += 1
        else:
            fork = kwargs.pop('fork', None)
            if isinstance(fork, hdict):
                maxlen = histo or fork.histo.maxlen
                self.histo = deque(fork.histo, maxlen) if maxlen else deque(fork.histo)
                self.pos = len(self.histo)
            else:
                self.histo = deque((self,), histo) if histo else deque((self,))
                self.pos = 1

    def previous(self):
        if self.pos > 0:
            return self.histo[self.pos - 1]

    def next(self):
        if self.pos < len(self.histo):
            return self.histo[self.pos + 1]

    def __add__(self, other):
        if not isinstance(other, dict):
            other = dict.fromkeys(other, dict.__default_value__)
        copy = hdict(self, histo=self.histo)
        dict.update(copy, other)
        return copy

    def clear(self):
        copy = hdict(self, histo=self.histo, pos=self.pos)
        dict.clear(copy)
        return copy

    def update(self, E={}, **F):
        copy = hdict(self, histo=self.histo, pos=self.pos)
        dict.update(copy, E, **F)
        return copy

    def fork(self):
        pass
