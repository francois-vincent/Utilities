
from functools import partial


def memoize_f(f):
    """ Memoization decorator for a function with positional args only
    """
    class memodict(dict):
        def __getitem__(self, *key):
            return dict.__getitem__(self, key)
        def __missing__(self, key):
            ret = self[key] = f(*key)
            return ret
    return memodict().__getitem__


class memoize(object):
    """ Memoization decorator for a method with positional args only
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.cache[args] = self.func(*args)
            return value
    def __doc__(self):
        return self.func.__doc__
    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


if __name__ == '__main__':
    class A(object):
        def __init__(self):
            self.x = 0
        @memoize
        def sum(self, *args):
            self.x += sum(args)
            return self.x

    a = A()
    assert a.sum(1, 2, 3) == 6
    assert a.sum(1, 2, 3) == 6
