
import pytest

from ..utilities import extract_translate, extract_dict, get_accessors_for_object
from ..converters_validators import convert_camelcase, clean_printables


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
        assert res == dict(A=1, B=2)

    def test_default_value(self):
        d = dict(a=1, b=2)
        res = extract_translate(d, self.trans, default=3)
        assert d == dict(a=1, b=2)
        assert res == dict(A=1, B=2, C=3)

    def test_remove(self):
        d = dict(a=1, b=2)
        res = extract_translate(d, self.trans, remove=True, default=None)
        assert d == {}
        assert res == dict(A=1, B=2, C=None)

    def test_raises(self):
        d = dict(a=1, b=2)
        with pytest.raises(KeyError):
            extract_translate(d, self.trans, default=Exception)


class TestExtractDict(object):
    keys = ('a', 'b', 'c')

    def test_default(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys)
        assert d == dict(a=1, b=2)
        assert res == dict(a=1, b=2)

    def test_default_value(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys, default=3)
        assert d == dict(a=1, b=2)
        assert res == dict(a=1, b=2, c=3)

    def test_remove(self):
        d = dict(a=1, b=2)
        res = extract_dict(d, self.keys, remove=True, default=None)
        assert d == {}
        assert res == dict(a=1, b=2, c=None)

    def test_raises(self):
        d = dict(a=1, b=2)
        with pytest.raises(KeyError):
            extract_dict(d, self.keys, default=Exception)


class TestConverters(object):

    def test_convert_camelcase(self):
        assert convert_camelcase('CamelCase') == 'camel_case'
        assert convert_camelcase('LongCamelCase') == 'long_camel_case'
        assert convert_camelcase('CamelCaseTBD') == 'camel_case_tbd'

    def test_clean_printables(self):
        printables = ''.join(chr(x) for x in xrange(32, 127))
        non_asciis = ''.join(chr(x) for x in xrange(256))
        assert clean_printables(non_asciis) == printables
        assert clean_printables('\x1f') == ''
        assert clean_printables('\x7f') == ''
