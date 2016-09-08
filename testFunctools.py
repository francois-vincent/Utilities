# -*- coding: utf-8 -*-

""" Some examples illustrating functools module usage
"""

from functools import partial, wraps, reduce


def sayincolor(text, color):
    print 'say "%s" in %s' % (text, color)

callback = partial(sayincolor, color='blue')
callback('hello')


def debug(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        res = func(*args,**kwargs)
        print("%s%s = %s" % (func.__name__, args, res))
        return res
    return wrapped


@debug
def add(x, y):
    return x + y

assert reduce(add, (1, 2, 3)) == 2 * 3
