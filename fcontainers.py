# -*- coding: utf-8 -*-
__version__ = '0.0.1'

# TODO
# tester différentes implémentations (speed) ex: set.contains_all iterator vs set arithmetic
# éventuellement mettre 2 implémentations avec un test (dict.__and__)
# design a purely immutable dict class with history stored in deque
# voir lodash.js pour d'autres idées
# trouver un moyen d'importer soit un remplacement (même nom), soit un autre nom
# tester en python 2 et python 3
# faire un repo dédié

__all__ = ['dict', 'list', 'set', 'DuplicateValueError']

from bisect import bisect_left
from collections import defaultdict, deque
from operator import add
import re

olddict = dict
oldlist = list
oldset = set


class DuplicateValueError(ValueError):
    pass


class UnknownOperatorError(ValueError):
    pass


class UnknownREFlagError(ValueError):
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


class Where(object):
    # Fixme voir django pour compléter les méthodes
    """
    Implements 'where' features for search in containers
    """

    def __init__(self, *terms):
        """ terms is a list of dictionaries
            representing a disjunction (or) of conjunctions (and)
        """
        self.terms = []
        for t in terms:
            term = []
            self.terms.append(term)
            for k, v in t.iteritems():
                try:
                    field, op = k.split('__')
                    op = self.operators[op]
                except ValueError:
                    field, op = k, self.equals
                except KeyError:
                    raise UnknownOperatorError("Operator '%s'" % op)
                term.append((field, op, v))

    def equals(self, record, field, value):
        return type(value)(record[field]) == value

    def notequals(self, record, field, value):
        return type(value)(record[field]) != value

    def gt(self, record, field, value):
        return type(value)(record[field]) > value

    def gte(self, record, field, value):
        return type(value)(record[field]) >= value

    def lt(self, record, field, value):
        return type(value)(record[field]) < value

    def lte(self, record, field, value):
        return type(value)(record[field]) <= value

    def inrange(self, record, field, value):
        lo, hi = value
        t = type(lo)
        assert t is type(hi)
        return lo <= t(record[field]) < hi

    def contains(self, record, field, value):
        return value in record[field]

    def icontains(self, record, field, value):
        return value in record[field].lower()

    def startswith(self, record, field, value):
        return record[field].startswith(value)

    def istartswith(self, record, field, value):
        return record[field].lower().startswith(value)

    def endswith(self, record, field, value):
        return record[field].endswith(value)

    def iendswith(self, record, field, value):
        return record[field].lower().endswith(value)

    def __call__(self, record):
        # Fixme tester ça
        return any(
            all(op(self, record, field, value) for field, op, value in t)
            for t in self.terms)

    operators = dict(
        equals=equals, eq=equals,
        notequals=notequals, neq=notequals,
        gt=gt, gte=gte, lt=lt, lte=lte,
        inrange=inrange,
        contains=contains,
        icontains=icontains,
        startswith=startswith,
        istartswith=istartswith,
        endswith=endswith,
        iendswith=iendswith,
    )


class RegExp(object):
    """ Implements Regulare expressions for searching into containers
    """

    def __init__(self, regexp, flags='', match=False):
        self.match = match
        re_flags = 0
        try:
            for f in flags.lower():
                re_flags |= self.flags_dict[f]
        except KeyError:
            raise UnknownREFlagError("Reg Exp flag %s unknown" % f)
        self.re = re.compile(regexp, re_flags)

    def __call__(self, record):
        if self.match:
            return self.re.match(record)
        return self.re.search(record)

    flags_dict = dict(
        a=re.A, i=re.I, l=re.L, m=re.M,
        s=re.S, u=re.U, x=re.X
    )


class dict(olddict):
    # Fixme: write complete doc
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

    # immutable methods (return another dict)

    def filter_key(self, f=bool, negate=False):
        """ Returns a copy of self filtered on keys that satisfy f
        """
        if negate:
            return {k: v for k, v in self.iteritems() if f(k)}
        else:
            return {k: v for k, v in self.iteritems() if f(k)}

    def filter_value(self, f=bool, negate=False):
        """ Returns a copy of self filtered on values that satisfy f
        """
        if negate:
            return {k: v for k, v in self.iteritems() if f(v)}
        else:
            return {k: v for k, v in self.iteritems() if f(v)}

    def filter(self, f=tuple, negate=False):
        """ Returns a copy of self filtered by f(key, value)
        """
        if negate:
            return {k: v for k, v in self.iteritems() if f(k, v)}
        else:
            return {k: v for k, v in self.iteritems() if f(k, v)}

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
        # Fixme: optimize
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
        """ True if every element of iterable is a key of self
        """
        return all(i in self for i in iterable)

    def contains_any(self, iterable):
        """ True if any element of iterable is a key of self
        """
        return any(i in self for i in iterable)

    def all_in(self, container):
        """ True if all keys of self are also in container
            use preferably if container.__contains__() evaluates in constant time
        """
        return all(i in container for i in self)

    def any_in(self, container):
        """ True if any key of self are also in container
            use preferably if container.__contains__() evaluates in constant time
        """
        return any(i in container for i in self)


class list(oldlist):
    # Fixme: write complete doc
    """
    Replacement class for list
    defines new methods that are both static and instance methods
    In place methods return 'self' instead of None
    - __add__: accepts any iterable, not only lists
    - __sub__: accepts any iterable, not only lists
    - __iadd__: does not need to be redefined, already accepts iterable !
    """
    list = oldlist

    # mutable methods (return self)

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

    __isub__ = discard_all

    # immutable methods (return another list)

    def filter(self, f=bool, negate=False):
        """ Returns a copy of self, retainning elements that satisfy f.
            You can specify f=Where(terms) to filter a list of dict,
        """
        if negate:
            return [x for x in self if not f(x)]
        else:
            return [x for x in self if f(x)]

    def __add__(self, iterable):
        return list(self).extend(iterable)

    def __sub__(self, iterable):
        return list(self).discard_all(iterable)

    # helper methods (return a value)

    def get(self, pos, default=None):
        try:
            return self[pos]
        except IndexError:
            return default

    def all_f(self, f=bool):
        """ True if all elements satisfy f
        """
        return all(f(x) for x in self)

    def any_f(self, f=bool):
        """ True if any element satisfy f
        """
        return any(f(x) for x in self)

    def reduce(self, f=bool):
        """ Returns the sum of the values of f calculated on each element
            if f returns a boolean, this counts the number of elements that satisfy f
        """
        return reduce(add, (f(x) for x in self))

    count = reduce

    def first_f(self, f=bool, negate=False):
        """ Returns the first element that satisfies f.
            You can specify f=Where(terms) to perform search a list of dict
        """
        if negate:
            for x in self:
                if not f(x):
                    return x
        else:
            for x in self:
                if f(x):
                    return x

    def index_b(self, value, start=0, stop=None):
        """ Performs binary search on sorted lists
        """
        if stop is None:
            stop = len(self)
        i = bisect_left(self, value, start, stop)
        if i < len(self) and self[i] == value:
            return i
        return -1

    def index_f(self, start=0, f=bool, negate=False):
        """ Returns the index of the first element that satisfies f
        """
        if negate:
            for i in xrange(start, len(self)):
                if not f(self[i]):
                    return i
            return -1
        else:
            for i in xrange(start, len(self)):
                if f(self[i]):
                    return i
            return -1


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
