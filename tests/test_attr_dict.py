# encoding: utf-8

import pytest

from ..attr_dict import ConfAttrDict


def test_simple_access():
    d = ConfAttrDict(a=1, b=2)
    assert len(d) == 2
    assert d['a'] == d.a
    assert d.a == 1
    assert d.b == 2
    assert d.update
    assert d.pull


def test_context_manager():
    d = ConfAttrDict(a=1, b=2)
    with d(a=10):
        assert len(d) == 2
        assert d.a == 10
        assert d.b == 2
    assert len(d) == 2
    assert d.a == 1
    assert d.b == 2


def test_context_manager_missing():
    d = ConfAttrDict(a=1, b=2)
    with d(c=3):
        assert len(d) == 3
        assert d.c == 3
    assert len(d) == 2
    assert d.a == 1
    assert d.b == 2
    with pytest.raises(AttributeError):
        d.c
