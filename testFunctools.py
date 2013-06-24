# -*- coding: utf-8 -*-

""" Some examples illustrating functools module usage
"""

__version__ = '0.0.1'
__date__ = '6/24/13'
__author__ = 'francois'
__mail__ = 'francois.vincent01@gmail.com'
__github__ = 'https://github.com/francois-vincent'

from functools import partial, wraps, reduce

def sayincolor(text, color):
    print 'say "%s" in %s' % (text, color)

callback = partial(sayincolor, color='blue')
callback('hello')

def debug(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        print("Calling '%s' with args %s" % (func.__name__, args))
        return func(*args,**kwargs)
    return wrapped

@debug
def add(x,y):
    return x+y

assert reduce(add, (1,2,3)) == 2*3
