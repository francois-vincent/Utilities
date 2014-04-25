# -*- coding: utf-8 -*-

# The simplest and most elegant way IMHO to make a closure that
# can modify its context and that is working in py2 and py3 as well.

import sys
if sys.version_info[0] == 3:
    raw_input = input


def make_authorize(message='proceed ? ', grant='yes', granted=False):
    outer = locals()
    def process():
        if outer['granted']:
            return True
        if raw_input(message) == grant:
            outer['granted'] = True
            return True
    return process

authorize = make_authorize()

if __name__ == '__main__':
    if authorize():
        print('authorize !')
    if authorize():
        print('authorize !')
