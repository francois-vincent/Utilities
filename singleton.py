# -*- coding: utf-8 -*-

"""
2 nice ways to handle singleton
"""

def singleton(cls):
	# the instance trick as list is ugly the fault is on python2.
	# with python3 I can use nonlocal variable
	instance =  []
	def getinstance(*args, **kwargs):
		if not instance:
			instance.append(cls(*args, **kwargs))
		return instance[0]
	return getinstance

class Singleton(type):
	def __init__(cls, *args, **kwargs):
		super(Singleton, cls).__init__(*args, **kwargs)
		cls.__instance = None
	def __call__(cls, *args, **kwargs):
		if cls.__instance is None:
			cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
		return cls.__instance

class MyClass(object):
	def __init__(self):
		print '__init__', self.__class__.__name__
MyClass()
MyClass()

@singleton
class MyClass2(MyClass):
	pass
MyClass2()
MyClass2()


class MyClass3(MyClass):
	__metaclass__ = Singleton
MyClass3()
MyClass3()
