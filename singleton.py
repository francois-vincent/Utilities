# -*- coding: utf-8 -*-

"""
2 nice ways to handle singleton
"""

__version__ = '0.1.0'
__date__    = 'jan 03rd, 2013'
__author__ = 'François Vincent'
__mail__ = 'fvincent@groupeseb.com'
__github__ = 'https://github.com/francois-vincent'

def singleton(cls):
    instance = None
    outer = locals()
    def getinstance(*args, **kwargs):
        if not outer['instance']:
            outer['instance'] = cls(*args, **kwargs)
        return outer['instance']
    return getinstance

class Singleton(type):
    __instance = None
    def __call__(cls, *args, **kwargs):
        if Singleton.__instance is None:
            Singleton.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return Singleton.__instance

class MyClass(object):
    def __init__(self):
        print '__init__', self.__class__.__name__
a = MyClass()
b = MyClass()
print a is b

@singleton
class MyClass2(MyClass):
    pass
a = MyClass2()
b = MyClass2()
print a is b


class MyClass3(MyClass):
    __metaclass__ = Singleton
a = MyClass3()
b = MyClass3()
print a is b
