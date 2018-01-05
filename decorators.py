

def memoize(f):
    """ Memoization decorator for a function with positional args only
    """
    class memodict(dict):
        def __getitem__(self, *key):
            return dict.__getitem__(self, key)
        def __missing__(self, key):
            ret = self[key] = f(*key)
            return ret
    return memodict().__getitem__


if __name__ == '__main__':
    class A(object):
        def __init__(self):
            self.x = 0
        @memoize
        def sum(self, *args):
            self.x += sum(*args)
            return self.x

    a = A()
    assert a.sum(1, 2, 3) == 6
    assert a.sum(1, 2, 3) == 6
