# -*- coding: utf-8 -*-

"""
test :
python toto.py
python toto.py | cat -
"""

import codecs, sys, locale

print locale.getdefaultlocale()
print locale.getlocale()

text = u'pi=\u03c0'
print sys.stdout.encoding
print sys.stdout.isatty()
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
print sys.stdout.encoding
print sys.stdout.isatty()
print text
