
import pytest

from ..utilities import extract_translate, SkipMissing, get_accessors_for_object


def test_default():
    d = dict(a=1, b=2)
    res = extract_translate(d, dict(a='A', b='B', c='C'))
    assert d == dict(a=1, b=2)
    assert res == dict(A=1, B=2, C=None)


def test_default_value():
    d = dict(a=1, b=2)
    res = extract_translate(d, dict(a='A', b='B', c='C'), default=3)
    assert d == dict(a=1, b=2)
    assert res == dict(A=1, B=2, C=3)


def test_remove():
    d = dict(a=1, b=2)
    res = extract_translate(d, dict(a='A', b='B', c='C'), remove=True)
    assert d == {}
    assert res == dict(A=1, B=2, C=None)


def test_raises():
    d = dict(a=1, b=2)
    with pytest.raises(KeyError):
        extract_translate(d, dict(a='A', b='B', c='C'), default=Exception)


def test_skip():
    d = dict(a=1, b=2)
    res = extract_translate(d, dict(a='A', b='B', c='C'), default=SkipMissing)
    assert d == dict(a=1, b=2)
    assert res == dict(A=1, B=2)


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
