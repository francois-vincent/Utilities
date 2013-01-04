# -*- coding: utf-8 -*-

# minimalist sorted set implemented as a list,
# with partial API of set, with bisection search.
# insertion is O(n) of course...

__version__ = '0.1.0'
__date__    = 'jan 03rd, 2013'
__author__ = 'François Vincent'
__mail__ = 'fvincent@groupeseb.com'
__github__ = 'https://github.com/francois-vincent'

from bisect import *

class sortedset(list):
    #* can contain mutable elements but can only contain mutually comparable elements
    def __init__(self, data=None):
        if data: self.update(data, False)
    def add(self, value):
        i = bisect(self, value)
        if i==0 or self[i-1] <> value: self.insert(i, value)
    def update(self, data, incremental=True):
        if incremental:
            for d in data:
                self.add(d)
        else:
            list.extend(self, set(data))
            self.sort()
    def index(self, value, start=0, stop=None):
        if stop is None: stop = len(self)
        i = bisect_left(self, value, start, stop)
        if i<len(self) and self[i] == value: return i
        raise ValueError('%s not in sortedset in range [%d, %d[' % (value, start, stop))
    def remove(self, value):
        i = bisect_left(self, value)
        if i<len(self) and self[i] == value: del self[i]
        raise ValueError('%s not in sortedset' % value)
    def discard(self, value):
        i = bisect_left(self, value)
        if i<len(self) and self[i] == value: del self[i]
    def count(self, value):
        return int(self.__contains__(value))
    def __contains__(self, value):
        i = bisect_left(self, value)
        return i<len(self) and self[i] == value

if __name__ == '__main__':
    l = ['1', '2', '3', '4', '5', '6']
    ss = sortedset(l)
    print ss
    print ss.index('4')
    print ss.index('4', 3)
    try: print ss.index('4', 4)
    except ValueError: print "index('4', 4): Value Error"
    print ss.index('4', 1, 4)
    print ss.index('4', 1, 3)
    try: print ss.index('4', 1, 2)
    except ValueError: print "index('4', 1, 2): Value Error"
    ss.remove('1')
    ss.remove('6')
    print ss
    try: ss.remove('8')
    except ValueError: print "remove('8'): Value Error"
