# -*- coding: utf-8 -*-

import inspect


class A(object):
    def a(self):
        print 'A.a()'
        return self


class B(object):
    def a(self):
        print 'B.a()'
        return self


def MixinFactory(name, base, *mixins):
    return type(name, (base,) + mixins, {})


C = MixinFactory('C', dict, A, B)
c = C()
print c.a()
print C.__bases__
print C.mro()
print inspect.getmro(C)

Z = MixinFactory('Z', dict, B, A)
z = Z()
print z.a()
print Z.__bases__
print Z.mro()
