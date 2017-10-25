
import pytest

from ..utilities import extract_translate, extract_dict, SkipMissing, get_accessors_for_object


def test_accessor_object():
    class A(object):
        a = 1
    x = A()
    get, set = get_accessors_for_object(A, x)
    assert get('a') == 1
    set('b', 2)
    assert get('a') == 1


def test_accessor_dict():
    class A(object):
        pass
    x = {'a': 1}
    get, set = get_accessors_for_object(A, x)
    assert get('a') == 1
    set('b', 2)
    assert get('a') == 1


class TestExtractTranslate(object):
    trans = dict(a='A', b='B', c='C')

    def test_default(self):
        d = dict(a=1, b=2)
        res = extract_translate(d, self.trans)
        assert d == dict(a=1, b=2)
        assert res == dict(A=1, B=2, C=None)

    def test_default_value(self):
        d = dict(a=1, b=2)
        res = extract_translate(d, self.trans, default=3)
        assert d == dict(a=1, b=2)
        assert res == dict(A=1, B=2, C=3)

    def test_remove(self):
        d = dict(a=1, b=2)
        res = extract_translate(d, self.trans, remove=True)
        assert d == {}
        assert res == dict(A=1, B=2, C=None)

    def test_raises(self):
        d = dict(a=1, b=2)
        with pytest.raises(KeyError):
            extract_translate(d, self.trans, default=Exception)

    def test_skip(self):
        d = dict(a=1, b=2)
        res = extract_translate(d, self.trans, default=SkipMissing)
        assert d == dict(a=1, b=2)
        assert res == dict(A=1, B=2)


class TestExtractDict(object):
    keys = ('a', 'b', 'c')

    def test_default(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys)
        assert d == dict(a=1, b=2)
        assert res == dict(a=1, b=2, c=None)

    def test_default_value(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys, default=3)
        assert d == dict(a=1, b=2)
        assert res == dict(a=1, b=2, c=3)

    def test_remove(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys, remove=True)
        assert d == {}
        assert res == dict(a=1, b=2, c=None)

    def test_raises(self):
        d = dict(a=1, b=2)
        with pytest.raises(KeyError):
            extract_dict(d, self.keys, default=Exception)

    def test_skip(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys, default=SkipMissing)
        assert d == dict(a=1, b=2)
        assert res == dict(a=1, b=2)
