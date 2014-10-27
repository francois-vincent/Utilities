# -*- coding: utf-8 -*-

# TODO
# dict: est-il pertinent d'avoir une autre valeur par défaut pour dict.fromkeys

__all__ = ['dict', 'list', 'set', 'DuplicateValueError']

olddict = dict
oldlist = list
oldset = set


class DuplicateValueError(ValueError):
    pass


class ReverseDictFactory(object):
    from collections import defaultdict

    class NoneObject(object):
        pass

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
            self.value = ReverseDictFactory.NoneObject
        def add(self, k, v):
            if self.value is not ReverseDictFactory.NoneObject:
                raise DuplicateValueError("Duplicate value '%s' found for keys '%s' and '%s'" % (v, k, self.value))
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

    def update_difference(self, mapping):
        for k, v in mapping.iteritems():
            if k in self:
                continue
            self[k] = v
        return self

    def discard(self, elt):
        if elt in self:
            self.__delitem__(elt)
        return self

    def discard_all(self, iterable):
        for k in iterable:
            if k in self:
                self.__delitem__(k)
        return self

    def remove(self, elt):
        self.__delitem__(elt)
        return self

    def remove_all(self, iterable):
        for k in iterable:
            self.__delitem__(k)
        return self

    def contains_all(self, iterable):
        return all(i in self for i in iterable)

    def contains_any(self, iterable):
        return any(i in self for i in iterable)

    def project(self, iterable):
        for k in set(self) - set(iterable):
            self.__delitem__(k)
        return self

    def reverse(self, duplicate=None):
        """ reverse the dictionary (exchange keys and values)
            what's happening to duplicate values ?
            if duplicate = None, an arbitrary value among duplicates is chosen (fastest)
            if duplicate = 'raise', raise a detailed DuplicateValueError exception
            if duplicate = 'count', count number of keys (for duplicates, this number is >1)
            if duplicate == 'list', append keys in a list
        """
        if not duplicate:
            return dict((v, k) for k, v in self.iteritems())
        data = ReverseDictFactory.get_dict(duplicate)
        for k, v in self.iteritems():
            data[v].add(k, v)
        return {k: v.val() for k, v in data.iteritems()}

    def add_difference(self, other):
        if not issubclass(other.__class__, dict.dict):
            other = dict.fromkeys(other)
        return dict(self).update_difference(other)

    def __add__(self, other):
        if not issubclass(other.__class__, dict.dict):
            other = dict.fromkeys(other)
        return dict(self).update(other)

    def __sub__(self, other):
        return dict(self).discard_all(other)

    def __and__(self, other):
        if len(other) > len(self) and issubclass(other.__class__, dict.dict):
            return {k: v for k, v in self.iteritems() if k in other}
        else:
            return {k: self[k] for k in other if k in self}

    def __iadd__(self, other):
        if not issubclass(other.__class__, dict.dict):
            other = dict.fromkeys(other)
        return self.update(other)

    __isub__ = discard_all
    __iand__ = __imul__ = project
    __or__ = __add__
    __ior__ = __iadd__
    __mul__ = __and__


class list(oldlist):
    """
    Replacement class for list
    In place methods return 'self' instead of None
    - __add__: accepts any iterable, not only lists
    - __sub__: accepts any iterable, not only lists
    - __iadd__: does not need to be redefined, already accepts iterable !
    """
    list = oldlist

    def clear(self):
        for x in xrange(len(self)):
            del self[-1]

    def append(self, x):
        oldlist.append(self, x)
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

    def discard(self, value):
        try:
            oldlist.remove(self, value)
        except ValueError:
            pass
        return self

    def remove_all(self, iterable):
        for i in iterable:
            oldlist.remove(self, i)
        return self

    def discard_all(self, iterable):
        for i in iterable:
            self.discard(i)
        return self

    def reverse(self):
        oldlist.reverse()
        return self

    def sort(self, **p):
        oldlist.sort(self, **p)
        return self

    def __add__(self, iterable):
        return list(self).extend(iterable)

    def __sub__(self, iterable):
        return list(self).discard_all(iterable)

    __isub__ = discard_all


class set(oldset):
    """
    Replacement class for set
    In place methods return 'self' instead of None
    - __iadd__: accepts any iterable, not only lists
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

    def contains_all(self, iterable):
        return all(i in self for i in iterable)

    def contains_any(self, iterable):
        return any(i in self for i in iterable)

    def __or__(self, iterable):
        return set(self).update(iterable)

    __add__ = __or__
    __iadd__ = __ior__ = update
