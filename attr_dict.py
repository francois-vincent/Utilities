# encoding: utf-8


class ConfAttrDict(dict):
    """
    A configuration attribute dictionary with a context manager that allows to push and pull items,
    eg for configuration overriding.
    """
    class __void__: pass
    class __raises__: pass
    _raises = __raises__

    def __getattr__(self, item):
        if item in self:
            return self[item]
        if self._raises is ConfAttrDict.__raises__:
            raise AttributeError("{} attribute not found: {}".format(self.__class__.__name__, item))
        return self._raises

    def copy(self):
        return ConfAttrDict(self)

    def update(self, E=None, **F):
        dict.update(self, E, **F)
        return self

    def __iadd__(self, other):
        return self.update(other)

    def __add__(self, other):
        return ConfAttrDict(self).update(other)

    def __isub__(self, other):
        for k in other:
            if k in self:
                del self[k]
        return self

    def __sub__(self, other):
        return ConfAttrDict(self).__isub__(other)

    def _push(self, **kwargs):
        if not hasattr(self, '__item_stack'):
            self.__item_stack = []
            self.__missing_stack = []
        self.__item_stack.append({k: self[k] for k in kwargs if k in self})
        kkwargs = kwargs
        for k in kwargs:
            if kwargs[k] is ConfAttrDict.__void__:
                if kkwargs is kwargs:
                    kkwargs = dict(kwargs)
                del kkwargs[k]
                if k in self:
                    del self[k]
        self.__missing_stack.append([k for k in kkwargs if k not in self])
        return self.update(kkwargs)

    def _pull(self):
        for k in self.__missing_stack.pop():
            del self[k]
        return self.update(self.__item_stack.pop())

    def __call__(self, **kwargs):
        return self._push(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._pull()
