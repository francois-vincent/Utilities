# -*- coding: utf-8 -*-

olddict = dict
oldlist = list


class dict(olddict):
    """
    Replacement class for dict
    In place methods returns 'self' instead of None
    New methods and operators:
    - remove: delete keys from an iterable
    - project: keep only keys in iterable
    - __add__; returns new dictionary, composed of a copy this dictionary updated with other, or updated with a dict.fromkey(other)
    - __sub__: operator version of remove
    - __and__: returns new dictionary, with keys not in other removed (projection)
    - __iadd__: update this with other, or with a dict.fromkey(other), identical to update if other is a dict
    - __isub__: operator version of remove
    """
    olddict = olddict

    def clear(self):
        dict.olddict.clear()
        return self

    def update(self, E={}, **F):
        dict.olddict.update(self, E, **F)
        return self

    def remove(self, iterable):
        for k in iterable:
            if k in self:
                self.__delitem__(k)
        return self

    def project(self, iterable):
        for k in self:
            if k not in set(iterable):
                self.__delitem__(k)
        return self

    def __add__(self, other):
        if not issubclass(other.__class__, dict):
            other = dict.fromkeys(other)
        return dict(self).update(other)

    def __sub__(self, other):
        return dict(self).remove(other)

    def __and__(self, other):
        return {k: self[k] for k in other}

    def __iadd__(self, other):
        if not issubclass(other.__class__, dict):
            other = dict.fromkeys(other)
        return self.update(other)

    __isub__ = remove
    __iand__ = project


class list(oldlist):
    """
    Replacement class for list
    In place methods returns 'self' instead of None
    """
    oldlist = oldlist

    def append(self, x):
        list.oldlist.append(x)
        return self

    def extend(self, iterable):
        list.oldlist.extend(self, iterable)
        return self

    def insert(self, i, x):
        if i < 0:
            if i == -1:
                return self.append(x)
            i += 1
        list.oldlist.insert(self, i, x)
        return self

    def remove(self, value):
        list.oldlist.remove(self, value)
        return self

    def reverse(self):
        list.oldlist.reverse()
        return self

    def sort(self, **p):
        list.oldlist.sort(self, **p)
        return self

    def __add__(self, iterable):
        return list(self).extend(iterable)

del olddict
del oldlist