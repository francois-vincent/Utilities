
from __future__ import print_function

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


class BaseSingleton(object):
    """
    Mixin with __new__
    """
    # TODO does not really work as __init__ is called again !
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            print("****call_new")
            cls._instance = super(BaseSingleton, cls).__new__(cls)
            return cls._instance


if __name__ == '__main__':
    class MyClass(object):
        def __init__(self):
            print('__init__', self.__class__.__name__)
    a = MyClass()
    b = MyClass()
    print('MyClass:', a is b)

    @singleton
    class MyClass2(MyClass):
        pass
    a = MyClass2()
    b = MyClass2()
    print('MyClass2:', a is b)

    class MyClass3(MyClass):
        __metaclass__ = _singleton
    a = MyClass3()
    b = MyClass3()
    print('MyClass3:', a is b)

    class MyClass4(Singleton, MyClass):
        pass
    a = MyClass4.get_instance()
    b = MyClass4.get_instance()
    print('MyClass4:', a is b)

    class MyClass5(BaseSingleton, MyClass):
        pass
    a = MyClass5()
    b = MyClass5()
    print('MyClass5:', a is b)
