# Copyright 2016 Kosc Telecom


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
