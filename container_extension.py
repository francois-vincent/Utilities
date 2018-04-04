# coding: utf-8


class ListMixin(object):

    def _check_attr(self):
        if len(self) and not hasattr(self[0], self._attr):
            raise AttributeError("Members of %s instance have no attribute '%s'" % (self.__class__.__name__, self._attr))

    def __getattr__(self, item):
        try:
            return self.__getattribute__(item)
        except AttributeError:
            self._attr = item
            self._check_attr()
            return self

    def __add__(self, other):
        try:
            return list.__add__(self, other)
        except TypeError:
            self._attr = '__add__'
            self._check_attr()
            return [x + other for x in self]

    def __call__(self, *args, **kwargs):
        return [getattr(x, self._attr)(*args, **kwargs) for x in self]


class MyList(ListMixin, list):
    def __init__(self, *args):
        list.__init__(self, args) if len(args) > 1 else list.__init__(self, args[0])


if __name__ == '__main__':
    l = MyList(2, 4)
    print(l + 1)
    l = MyList('TOTO', 'Titi')
    print(l.lower())
    print(l.title())
    l.toto()
