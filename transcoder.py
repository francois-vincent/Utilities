# -*- coding: utf-8 -*-

# rewrites a text file from source-encoding to target-encoding

__version__ = '0.1.0'
__date__    = 'jan 04th, 2013'
__author__ = 'François Vincent'
__mail__ = 'fvincent@groupeseb.com'
__github__ = 'https://github.com/francois-vincent'

import sys, os
import codecs

if len(sys.argv) <> 4:
    print 'Usage:', sys.argv[0], '<filename> <source-encoding> <target-encoding>'
    sys.exit()
filename = sys.argv[1]
if not os.access(filename, os.W_OK):
    print 'Nonexistent or non-writable file', filename
    sys.exit()
fromencoding = sys.argv[2]
toencoding = sys.argv[3]
try:
    codecs.lookup(fromencoding)
except LookupError:
    print "can't find source encoding", fromencoding
    sys.exit()
try:
    codecs.lookup(toencoding)
except LookupError:
    print "can't find target encoding", toencoding
    sys.exit()

with open(filename, 'rb+') as f:
    data = f.read()
    data = data.decode(fromencoding).encode(toencoding)
    f.seek(0)
    f.write(data)
    f.truncate()
