
import pytest

from ..utilities import extract_translate, SkipMissing


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
