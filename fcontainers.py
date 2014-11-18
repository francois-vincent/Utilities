# -*- coding: utf-8 -*-
__version__ = '0.0.1'

# TODO
# draw a clear line between mutable and immutable methods
# tester différentes implémentations (speed) ex: set.contains_all iterator vs set arithmetic
# éventuellement mettre 2 implémentations avec un test (dict.__and__)
# design a purely immutable dict class with history stored in deque
# voir lodash.js pour d'autres idées

__all__ = ['dict', 'list', 'set', 'DuplicateValueError']

from collections import defaultdict, deque

olddict = dict
oldlist = list
oldset = set


class DuplicateValueError(ValueError):
    pass


class ReverseDictFactory(object):
    """
    Helper class for dict.reverse()
    """

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
        return defaultdict({
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
    __default_value__ = None

    # mutable methods (return self)

    def clear(self):
        olddict.clear(self)
        return self

    def update(self, E={}, **F):
        """ Update replacement that retuurns sel
        """
        olddict.update(self, E, **F)
        return self

    def update_difference(self, mapping):
        """ Like update except that only new keys will be updated
        """
        for k, v in mapping.iteritems():
            if k in self:
                continue
            self[k] = v
        return self

    def discard(self, elt):
        """ Like delete except it does not raise KeyError exception
        """
        if elt in self:
            self.__delitem__(elt)
        return self

    def discard_all(self, iterable):
        """ Iterable version of discard
        """
        for k in iterable:
            if k in self:
                self.__delitem__(k)
        return self

    def remove(self, elt):
        """ Alias of delete that returns self
        """
        self.__delitem__(elt)
        return self

    def remove_all(self, iterable):
        """ iterable version of remove
        """
        for k in iterable:
            self.__delitem__(k)
        return self

    def project(self, iterable):
        """ Removes every key of self that is not in iterable
        """
        for k in set(self) - set(iterable):
            self.__delitem__(k)
        return self

    def __iadd__(self, other):
        """ Like update, except that it can add any iterable
        """
        if not isinstance(other, olddict):
            other = dict.fromkeys(other, dict.__default_value__)
        return self.update(other)

    __ior__ = __iadd__
    __isub__ = discard_all
    __iand__ = __imul__ = project

    # immutable methods (return a copy)

    def filter_key(self, f=bool):
        """ Returns a copy of self filtered on keys that satisfy f
        """
        return {k: v for k, v in self.iteritems() if f(k)}

    def filter_value(self, f=bool):
        """ Returns a copy of self filtered on values that satisfy f
        """
        return {k: v for k, v in self.iteritems() if f(v)}

    def filter(self, f=tuple):
        """ Returns a copy of self filtered by f(key, value)
        """
        return {k: v for k, v in self.iteritems() if f(k, v)}

    def search(self, text):
        """ Returns a copy of self filtered on keys that contain the search text
        """
        return {k: v for k, v in self.iteritems() if text in k}

    def reverse(self, duplicate=None):
        """ reverse the dictionary (exchange keys and values)
            what's happening to duplicate values ?
            if duplicate == None, an arbitrary value among duplicates is chosen (fastest)
            if duplicate == 'raise', raise a detailed DuplicateValueError exception
            if duplicate == 'count', count number of keys (for duplicates, this number is >1)
            if duplicate == 'list', append keys in a list
        """
        if not duplicate:
            return {v: k for k, v in self.iteritems()}
        data = ReverseDictFactory.get_dict(duplicate)
        for k, v in self.iteritems():
            data[v].add(k, v)
        return {k: v.val() for k, v in data.iteritems()}

    def add_difference(self, other):
        """ Immutable version of update_difference, that can add any iterable
        """
        if not isinstance(other, olddict):
            other = dict.fromkeys(other, dict.__default_value__)
        return dict(self).update_difference(other)

    def __add__(self, other):
        """ Immutable version of update, that can add any iterable
        """
        if not isinstance(other, olddict):
            other = dict.fromkeys(other, dict.__default_value__)
        return dict(self).update(other)

    def __sub__(self, other):
        """ Immutable version of discard_all
        """
        return dict(self).discard_all(other)

    def __and__(self, other):
        """ Immutable version of project, with optimization based on the relative size
        """
        if len(other) > len(self) and isinstance(other, olddict):
            return {k: v for k, v in self.iteritems() if k in other}
        else:
            return {k: self[k] for k in other if k in self}

    __or__ = __add__
    __mul__ = __and__

    # helper methods (return a value)

    def contains_all(self, iterable):
        """ True if every element of iterable is aalso a key of self
        """
        return all(i in self for i in iterable)

    def contains_any(self, iterable):
        """ True if any element of iterable is aalso a key of self
        """
        return any(i in self for i in iterable)

    def all_in(self, container):
        """ True if all keys of self is also in container
            use preferably if container.__contains__() evaluates in constant time
        """
        return all(i in container for i in self)

    def any_in(self, container):
        """ True if any key of self is also in container
            use preferably if container.__contains__() evaluates in constant time
        """
        return any(i in container for i in self)


class list(oldlist):
    # Fixme: sort methods by type
    """
    Replacement class for list
    defines new methods that are both static and instance methods
    In place methods return 'self' instead of None
    - __add__: accepts any iterable, not only lists
    - __sub__: accepts any iterable, not only lists
    - __iadd__: does not need to be redefined, already accepts iterable !
    """
    list = oldlist

    def all_none(self):
        return all(x is None for x in self)

    def any_none(self):
        return any(x is None for x in self)

    def all_f(self, f=bool):
        return all(f(x) for x in self)

    def any_f(self, f=bool):
        return any(f(x) for x in self)

    def first_not_none(self):
        for x in self:
            if x is not None:
                return x

    def first_f(self, f=bool):
        for x in self:
            if f(x):
                return x

    def index_f(self, f=bool):
        for i, x in enumerate(self):
            if f(x):
                return i
        return -1

    def clear(self):
        del self[:]
        return self

    def append(self, x):
        oldlist.append(self, x)
        return self

    def extend(self, iterable):
        oldlist.extend(self, iterable)
        return self

    def insert(self, i, x):
        """ corrects negative index origin of original insert that can not append
        """
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

    def search(self, text):
        return [x for x in self if text in x]

    def __add__(self, iterable):
        return list(self).extend(iterable)

    def __sub__(self, iterable):
        return list(self).discard_all(iterable)

    __isub__ = discard_all


class set(oldset):
    # Fixme: sort methods by type, complete methods set
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

    def search(self, text):
        set(x for x in self if text in x)

    def __or__(self, iterable):
        return set(self).update(iterable)

    __add__ = __or__
    __iadd__ = __ior__ = update


class hdict(olddict):
    # Fixme: specify first
    """ hdict (history dict) is a kinnd of immutable dict that preserves its history
        history is stored in a deque
    """
    def __init__(self, *args, **kwargs):
        """ if histo is a deque, extend the currunt history, eventually erasing future states
            if histi is None or an int, create a new instance
        """
        histo = kwargs.pop('histo', None)
        dict.__init__(self, *args, **kwargs)
        if isinstance(histo, deque):
            self.histo = histo
            self.pos = kwargs.pop('pos')
            if self.pos < len(histo):
                # Fixme truncate end of deque
                histo[self.pos] = self
            else:
                histo.append(self)
            self.pos += 1
        else:
            fork = kwargs.pop('fork', None)
            if isinstance(fork, hdict):
                maxlen = histo or fork.histo.maxlen
                self.histo = deque(fork.histo, maxlen) if maxlen else deque(fork.histo)
                self.pos = len(self.histo)
            else:
                self.histo = deque((self,), histo) if histo else deque((self,))
                self.pos = 1

    def previous(self):
        if self.pos > 0:
            return self.histo[self.pos - 1]

    def next(self):
        if self.pos < len(self.histo):
            return self.histo[self.pos + 1]

    def __add__(self, other):
        if not isinstance(other, olddict):
            other = dict.fromkeys(other, dict.__default_value__)
        copy = hdict(self, histo=self.histo)
        olddict.update(copy, other)
        return copy

    def clear(self):
        copy = hdict(self, histo=self.histo, pos=self.pos)
        olddict.clear(copy)
        return copy

    def update(self, E={}, **F):
        copy = hdict(self, histo=self.histo, pos=self.pos)
        olddict.update(copy, E, **F)
        return copy

    def fork(self):
        pass
