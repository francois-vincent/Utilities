# -*- coding: utf-8 -*-

from fcontainers import *
import unittest


class DictTestCase(unittest.TestCase):

    def setUp(self):
        self.d = dict(a=1, b=2, c=3, d=4)

    def test_constructor(self):
        d = self.d
        self.assertDictEqual(dict(d), d)
        self.assertDictEqual(dict(d, **d), d)

    def test_clear(self):
        d = self.d
        self.assertDictEqual(d.clear(), {})

    def test_update(self):
        d = self.d
        self.assertDictEqual(dict().update(d), d)
        self.assertDictEqual(dict().update(**d), d)
        self.assertDictEqual(dict().update(d, **d), d)

    def test_discard(self):
        d = self.d
        self.assertDictEqual(d.discard('a'), dict(b=2, c=3, d=4))
        self.assertDictEqual(d, dict(b=2, c=3, d=4))
        self.assertDictEqual(d.discard('e'), dict(b=2, c=3, d=4))

    def test_discard_all(self):
        d = self.d
        self.assertDictEqual(d.discard_all('ad'), dict(b=2, c=3))
        self.assertDictEqual(d, dict(b=2, c=3))
        self.assertDictEqual(d.discard_all('bef'), dict(c=3))

    def test_remove(self):
        d = self.d
        self.assertDictEqual(d.remove('a'), dict(b=2, c=3, d=4))
        self.assertDictEqual(d, dict(b=2, c=3, d=4))
        self.assertRaises(KeyError, d.remove, 'e')

    def test_remove_all(self):
        d = self.d
        self.assertDictEqual(d.remove_all('ad'), dict(b=2, c=3))
        self.assertDictEqual(d, dict(b=2, c=3))
        self.assertRaises(KeyError, d.remove_all, 'bef')

    def test_contains_all(self):
        d = self.d
        self.assertTrue(d.contains_all('ab'))
        self.assertTrue(d.contains_all('abcd'))
        self.assertFalse(d.contains_all('abce'))

    def test_contains_any(self):
        d = self.d
        self.assertTrue(d.contains_any('defg'))
        self.assertFalse(d.contains_any('xyz'))

    def test_project(self):
        d = self.d
        self.assertDictEqual(d.project('bc'), dict(b=2, c=3))
        self.assertDictEqual(d, dict(b=2, c=3))
        self.assertDictEqual(d.project('bc'), dict(b=2, c=3))
        self.assertDictEqual(d.project('ad'), {})

    def test_reverse_noduplicate(self):
        d = dict(self.d)
        self.assertDictEqual(d.reverse(), {1: 'a', 2: 'b', 3: 'c', 4: 'd'})
        self.assertDictEqual(d, self.d)
        self.assertDictEqual(d.reverse().reverse(), self.d)

    def test_reverse_duplicate_noraise(self):
        d = self.d + dict(e=1)
        self.assertDictEqual(d.reverse() & (2, 3, 4), {2: 'b', 3: 'c', 4: 'd'})
        self.assertIn(d.reverse()[1], ('a', 'e'))

    def test_reverse_duplicate_raise(self):
        d = self.d + dict(e=1)
        self.assertRaises(DuplicateValueError, d.reverse, 'raise')

    def test_reverse_duplicate_count(self):
        d = self.d + dict(e=1)
        self.assertDictEqual(d.reverse('count'), {1: 2, 2: 1, 3: 1, 4: 1})

    def test_reverse_duplicate_list(self):
        d = self.d + dict(e=1)
        self.assertDictEqual(d.reverse('list'), {1: ['a', 'e'], 2: ['b'], 3: ['c'], 4: ['d']})

    def test_add(self):
        d = dict(self.d)
        self.assertDictEqual(d + 'ae', {'a': None, 'b': 2, 'c': 3, 'd': 4, 'e': None})
        self.assertDictEqual(d, self.d)

    def test_sub(self):
        d = dict(self.d)
        self.assertDictEqual(d - 'ad', dict(b=2, c=3))
        self.assertDictEqual(d, self.d)
        self.assertDictEqual(d - 'adef', dict(b=2, c=3))

    def test_and(self):
        d = dict(self.d)
        self.assertDictEqual(d & 'bc', dict(b=2, c=3))
        self.assertDictEqual(d, self.d)
        self.assertDictEqual(d & 'ef', {})

    def test_iadd(self):
        d = self.d
        d += 'ae'
        self.assertDictEqual(d, {'a': None, 'b': 2, 'c': 3, 'd': 4, 'e': None})

    def test_isub(self):
        d = self.d
        d -= 'ad'
        self.assertDictEqual(d, dict(b=2, c=3))


class ListTestCase(unittest.TestCase):

    def test_constructor(self):
        self.assertListEqual(list('abcd'), ['a', 'b', 'c', 'd'])
        self.assertListEqual(list(list('abcd')), ['a', 'b', 'c', 'd'])


class SetTestCase(unittest.TestCase):

    def test_constructor(self):
        self.assertSetEqual(set('abcd'), set(['a', 'b', 'c', 'd']))
        self.assertSetEqual(set(set('abcd')), set(['a', 'b', 'c', 'd']))


if __name__ == '__main__':
    unittest.main()