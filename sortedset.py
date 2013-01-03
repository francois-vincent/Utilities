# -*- coding: utf-8 -*-

from bisect import *

class sortedset(list):
	#* can contain mutable elements but can only contain mutually comparable elements
	def __init__(self, data=None, process=True):
		if data: self.extend(data, process)
	def append(self, value):
		i = bisect(self, value)
		if i==0 or self[i-1] <> value: self.insert(i, value)
	def extend(self, data, process=True):
		if process:
			list.extend(self, set(data))
			self.sort()
		else: list.extend(self, data)
	def index(self, value, start=0, stop=None):
		if stop is None: stop = len(self)
		i = bisect_left(self, value, start, stop)
		if i<len(self) and self[i] == value: return i
		raise ValueError('sortedset.index(x): x not in sortedset')
	def remove(self, value):
		i = bisect_left(self, value)
		if i<len(self) and self[i] == value: del self[i]
		else: raise ValueError('sortedset.remove(x): x not in sortedset')

if __name__ == '__main__':
	l = ['1', '2','3','4','5','6']
	ss = sortedset(l)
	print ss
	print ss.index('4')
	print ss.index('4', 3)
	try: print ss.index('4', 4)
	except ValueError: print "index('4', 4): Value Error"
	print ss.index('4', 1, 4)
	print ss.index('4', 1, 3)
	try: print ss.index('4', 1, 2)
	except ValueError: print "index('4', 1, 2): Value Error"
	ss.remove('1')
	ss.remove('6')
	print ss
	try: ss.remove('8')
	except ValueError: print "remove('8'): Value Error"
