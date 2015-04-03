# -*- coding: utf-8 -*-

from __future__ import print_function


def pipize(f):
    class op(object):
        def __ror__(self, o):
            return f(o)
    return op()


@pipize
def Op1(o):
    return '__' + o


@pipize
def Op2(o):
    return o + '__'


if __name__ == '__main__':
    print('x' | Op1 | Op2)
