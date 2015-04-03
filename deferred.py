# -*- coding: utf-8 -*-


def deferred(func):
    def wrapped(*args, **kwargs):
        def inner():
            return func(*args, **kwargs)
        return inner
    return wrapped


if __name__ == '__main__':
    @deferred
    def add(a, b):
        return a + b

    x = add(1, 2)
    print x
    print x()