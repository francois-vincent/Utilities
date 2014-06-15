# -*- coding: utf-8 -*-

"""
3 different ways to handle singleton.
A decorator, a metaclass and a mixin/factory.
"""


def singleton(cls):
    """
    Class decorator
    TODO: use args and kwargs as key to instance dict
    """
    outer = locals()
    def getinstance(*args, **kwargs):
        if 'instance' not in outer:
            outer['instance'] = cls(*args, **kwargs)
        return outer['instance']
    return getinstance


class _singleton(type):
    """
    Metaclass
    """
    __instance = None
    def __call__(cls, *args, **kwargs):
        if _singleton.__instance is None:
            _singleton.__instance = super(_singleton, cls).__call__(*args, **kwargs)
        return _singleton.__instance


class Singleton(object):
    """
    Mixin with factory
    """
    _instance = None
    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)
        return cls._instance


if __name__ == '__main__':
    class MyClass(object):
        def __init__(self):
            print '__init__', self.__class__.__name__
    a = MyClass()
    b = MyClass()
    print 'Singleton:', a is b

    @singleton
    class MyClass2(MyClass):
        pass
    a = MyClass2()
    b = MyClass2()
    print 'Singleton:', a is b

    class MyClass3(MyClass):
        __metaclass__ = _singleton
    a = MyClass3()
    b = MyClass3()
    print 'Singleton:', a is b

    class MyClass4(Singleton, MyClass):
        pass
    a = MyClass4.get_instance()
    b = MyClass4.get_instance()
    print 'Singleton:', a is b
