# -*- coding: utf-8 -*-

olddict = dict
oldlist = list


class dict(olddict):
    """
    Replacement class for dict
    In place methods returns 'self' instead of None
    """
    olddict = olddict

    def clear(self):
        dict.olddict.clear()
        return self

    def update(self, E=None, **F):
        dict.olddict.update(self, E, **F) if E else dict.olddict.update(self, **F)
        return self

    def remove(self, iterable):
        for k in iterable:
            if k in self:
                self.__delitem__(k)
        return self

    def __add__(self, other):
        if issubclass(other.__class__, dict):
            return dict(self).update(other)
        else:
            return dict(self).update(dict.fromkeys(other))

    def __sub__(self, other):
        return dict(self).remove(other)

    def __iadd__(self, other):
        if issubclass(other.__class__, dict):
            return self.update(other)
        else:
            return self.update(dict.fromkeys(other))

    __isub__ = remove


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