# encoding: utf-8

import pytest

from ..fabric_utils import run_sequence, collapse_op, collapse_self, set_method, set_methods_from_conf

def test_sequencer():
    class Toto(object):
        x = []
        def a(self):
            self.x.append('a')
        def b(self, p):
            self.x.append(('b', p))
        def c(self, p1, p2):
            self.x.append(('c', p1, p2))
        def d(self, *args):
            self.x.append(('d', args))
        def e(self, p, k=None):
            self.x.append(('e', p, k))
        def f(self, *args, **kwargs):
            self.x.append(('f', args, kwargs))

    toto = Toto()
    run_sequence(toto, 'a', ('b', 1), ('c', (1, 2)), ('d', (1, 2)),
                 ('e', (1, 2)), ('e', (1, ), {'k': 3}), ('f', (1, ), {'x': 2}))
    toto.x = ['a', ('b', 1), ('c', 1, 2), ('d', (1, 2)), ('e', 1, 2), ('e', 1, 3), ('f', (1,), {'x': 2})]


def test_decorators():
    class Test(object):
        hosts = {'h1': 'container1', 'h2': 'container2'}
        @collapse_op('dict')
        def get_hosts(self, host, a, b=None):
            return self.hosts[host]
        @collapse_self
        def get_self(self, host, *args, **kwargs):
            pass
        @collapse_op('and')
        def get_true(self, host):
            return True
        @collapse_op('append')
        def get_list(self, host):
            return self.hosts[host]

    t = Test()
    assert t.get_hosts('', host='h1') == Test.hosts['h1']
    assert t.get_hosts('') == Test.hosts
    assert t.get_self() is t
    assert t.get_self(host='h1') is t
    assert t.get_true() is True
    assert t.get_true(host='h1')
    assert set(t.get_list()) == set(Test.hosts.values())
    assert t.get_list(host='h1') == Test.hosts['h1']


def test_set_method():
    class Test(object):
        pass

    def toto(self, param):
        return param

    t = Test()
    with pytest.raises(AttributeError):
        t.toto(12)
    set_method(Test, toto)
    assert hasattr(Test, 'toto')
    assert hasattr(t, 'toto')
    assert t.toto(12) == 12


def test_set_methods_from_conf():
    class Test(object):
        default_deco = "collapse_op('dict')"
        hosts = {'h1': 'container1', 'h2': 'container2'}

    def toto(self, host, param):
        return param

    def titi(self, host, param):
        """[deco:collapse_op('and')]
        """
        return param

    conf = dict(toto=toto, titi=titi)
    set_methods_from_conf(Test, conf)
    assert Test().toto(12) == {'h1': 12, 'h2': 12}
    assert Test().titi(12) is True
