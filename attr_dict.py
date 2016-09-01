# encoding: utf-8


class ConfAttrDict(dict):
    """
    An configuration attribute dictionary with a context manager that allows to push and pull items,
    eg for configuration overriding.
    """

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError("{} attribute not found: {}".format(self.__class__.__name__, item))

    def push(self, **kwargs):
        if not hasattr(self, '__item_stack'):
            self.__item_stack = []
            self.__missing_stask = []
        self.__item_stack.append({k: self[k] for k in kwargs if k in self})
        self.__missing_stask.append([k for k in kwargs if k not in self])
        self.update(kwargs)
        return self

    def pull(self):
        self.update(self.__item_stack.pop())
        for k in self.__missing_stask.pop():
            del self[k]
        return self

    def __call__(self, **kwargs):
        return self.push(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.pull()
