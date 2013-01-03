# -*- coding: utf-8 -*-

class AutoMDDict(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

a = AutoMDDict()
a[1] = 'a'
a[2][1] = 'b'
a[3][2][1] = 'c'
print a
print type(a)
