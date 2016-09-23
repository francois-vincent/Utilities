# -*- coding: utf-8 -*-


class bdict(dict):
    """
    Better dict redifines update to return self.
    In a general way, each method that do not return a datum should return self, so as to allow method chaining.
    It also defines new methods:
    add() adds only new keys.
    remove() removes keys from parameter tuple/list.
    __add__() updates from lhs dict.
    __sub__() removes keys from lhs dict.
    """
    def update(self, E=None, **F):
        dict.update(self, E, **F) if E else dict.update(self, **F)
        return self

    def add(self, E=None, **F):
        return self.update(bdict().update(E, **F).__sub__(self))

    def remove(self, *keys):
        if len(keys) == 1 and hasattr(keys[0], '__iter__'):
            keys = keys[0]
        for k in keys:
            try:
                del self[k]
            except KeyError:
                pass
        return self

    def __add__(self, other):
        dict.update(self, other)
        return self

    def __sub__(self, other):
        for k in other:
            try:
                del self[k]
            except KeyError:
                pass
        return self


if __name__ == '__main__':
    d = bdict(a=1, b=2)
    d2 = dict(c=3)
    d3 = dict(d=4)
    assert 'c' in d.update(d2)
    d += d3
    assert d == {'a': 1, 'c': 3, 'b': 2, 'd': 4}
    d -= d2
    assert d == {'a': 1, 'b': 2, 'd': 4}
    d = bdict(dict(a=1, b=2), c=3)
    d.remove('a')
    assert d == {'c': 3, 'b': 2}
    d = bdict(a=1, b=2, c=3)
    d.remove('a', 'b')
    assert d == {'c': 3}
    d = bdict(a=1, b=2, c=3)
    d.remove(('a',))
    assert d == {'c': 3, 'b': 2}
    d = bdict(a=1, b=2, c=3)
    d.remove(('a', 'b'))
    assert d == {'c': 3}
    assert bdict(a=1, b=2).update(b=3, c=4) == {'a': 1, 'b': 3, 'c': 4}
    assert bdict(a=1, b=2).add(b=3, c=4) == {'a': 1, 'b': 2, 'c': 4}
