# -*- coding: utf-8 -*-

__all__ = ['dict', 'list', 'set', 'DuplicateValueError']


olddict = dict
oldlist = list
oldset = set


class DuplicateValueError(ValueError):
    pass


class ReverseDictFactory(object):
    from collections import defaultdict

    class _count(object):
        def __init__(self):
            self.value = 0
        def add(self, k, v):
            self.value += 1
        def val(self):
            return self.value

    class _list(list):
        def add(self, k, v):
            self.append(k)
        def val(self):
            return self

    class _raise(object):
        def __init__(self):
            self.value = None
        def add(self, k, v):
            if self.value is not None:
                raise DuplicateValueError("Duplicate value %s found for keys '%s' and '%s'" % (v, k, self.value))
            self.value = k
        def val(self):
            return self.value

    @classmethod
    def get_dict(cls, case):
        return cls.defaultdict({
            'raise': cls._raise,
            'count': cls._count,
            'list': cls._list,
        }[case])


class dict(olddict):
    """
    Replacement class for dict
    In place methods return 'self' instead of None
    New methods and operators:
    - remove: delete keys from an iterable
    - project: keep only keys in iterable
    - reverse: returns a new dictionary, with exchanged keys and values
    - __add__; returns new dictionary, composed of a copy this dictionary updated with other,
               or updated with a dict.fromkey(other)
    - __sub__: operator version of remove
    - __and__: returns new dictionary, with keys not in other removed (projection)
    - __iadd__: update this with other, or with a dict.fromkey(other), identical to update if other is a dict
    - __isub__: operator version of remove
    - __iand__: operator version of project
    """
    dict = olddict

    def clear(self):
        olddict.clear(self)
        return self

    def update(self, E={}, **F):
        olddict.update(self, E, **F)
        return self

    def remove(self, iterable):
        for k in iterable:
            if k in self:
                self.__delitem__(k)
        return self

    def project(self, iterable):
        for k in set(self) - set(iterable):
            self.__delitem__(k)
        return self

    def reverse(self, duplicate='silent'):
        """ reverse the dictionary (exchange keys and values)
            what's happening to duplicate values ?
            if duplicate = 'silent' an arbitrary value among duplicates is chosen
            if duplicate = 'raise', raise a DuplicateValueError exception
            if duplicate = 'count', count number of keys (if duplicates, this number is >1)
            if duplicate == 'list', append keys in a list
        """
        if duplicate == 'silent':
            return dict((v, k) for k, v in self.iteritems())
        data = ReverseDictFactory.get_dict(duplicate)
        for k, v in self.iteritems():
            data[v].add(k, v)
        return {k: v.val() for k, v in data.iteritems()}

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
    In place methods return 'self' instead of None
    - __add__: accepts any iterable, not only lists
    """
    list = oldlist

    def append(self, x):
        oldlist.append(x)
        return self

    def extend(self, iterable):
        oldlist.extend(self, iterable)
        return self

    def insert(self, i, x):
        if i < 0:
            if i == -1:
                return self.append(x)
            i += 1
        oldlist.insert(self, i, x)
        return self

    def remove(self, value):
        oldlist.remove(self, value)
        return self

    def reverse(self):
        oldlist.reverse()
        return self

    def sort(self, **p):
        oldlist.sort(self, **p)
        return self

    def __add__(self, iterable):
        return list(self).extend(iterable)


class set(oldset):
    """
    Replacement class for set
    In place methods return 'self' instead of None
    """
    set = oldset

    def add(self, item):
        oldset.add(item)
        return self

    def clear(self):
        oldset.clear(self)
        return self

    def update(self, iterable):
        oldset.update(self, set(iterable))
        return self

    __iadd__ = __ior__ = update
