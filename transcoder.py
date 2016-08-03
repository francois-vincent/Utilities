#! /usr/bin/env python

# rewrites a text file from source-encoding to target-encoding

import codecs
import glob
import os

from clingon import clingon


@clingon.clize
def transcoder(source, fromencoding, toencoding, rewrite=False, destination=''):
    """
    A text file converter utility written in python.
    Can convert from any supported python text code to any other one.
    """
    if rewrite and destination:
        print("You can't specify a destination together with option 'rewrite'")
        return 1

    if rewrite and not os.access(source, os.W_OK):
        print('Nonexistent or non-writable file ' + source)
        return 1
    if not os.access(source, os.R_OK):
        print('Missing file ' + source)
        return 1

    try:
        codecs.lookup(fromencoding)
    except LookupError:
        print("can't find source encoding " + fromencoding)
        return 1
    try:
        codecs.lookup(toencoding)
    except LookupError:
        print("can't find target encoding " + toencoding)
        return 1

    if rewrite:
        with open(source, 'rb+') as f:
            data = f.read()
            data = data.decode(fromencoding).encode(toencoding)
            f.seek(0)
            f.write(data)
            f.truncate()
        return

    if not destination:
        destination = max(glob.glob(source + '*')) + '.backup'
    with open(source, 'rb') as fs, open(destination, 'wb') as fd:
        data = fs.read()
        data = data.decode(fromencoding).encode(toencoding)
        fd.write(data)
