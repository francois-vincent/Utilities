
from collections import Counter
from itertools import cycle
import operator as ope

from ..deep_struct_ope import Condition, DeepStruct, deep_struct_collect, MirrorFactory


class TestStructConstruct:

    def test_simple_dict(self):
        struct = DeepStruct().construct('a')
        assert struct == {'a': None}
        struct = DeepStruct().construct('a.b')
        assert struct == {'a': {'b': None}}

    def test_multiple_dict(self):
        struct = DeepStruct().construct('a,b')
        assert struct == {'a': None, 'b': None}
        struct = DeepStruct().construct('a,b.c,d')
        assert struct == {'a': {'c': None, 'd': None}, 'b': None}

    def test_dict_mirror_factory(self):
        struct = DeepStruct(MirrorFactory).construct('a,b.c,d')
        assert struct == {'a': {'c': 'c', 'd': 'd'}, 'b': 'b'}

    def test_list(self):
        struct = DeepStruct().construct('[2]')
        assert struct == [None, None]
        struct = DeepStruct().construct('[1].[1].[3]')
        assert struct == [[[None, None, None]]]

    def test_list_mirror_factory(self):
        struct = DeepStruct(MirrorFactory).construct('[2]')
        assert struct == [0, 1]
        struct = DeepStruct(MirrorFactory).construct('[1].[1].[3]')
        assert struct == [[[0, 1, 2]]]

    def test_mixed(self):
        struct = DeepStruct().construct('[2].a')
        assert struct == [{'a': None}, None]
        struct = DeepStruct().construct('a.[2].b,c.[2]')
        assert struct == {'a': [{'b': [None, None], 'c': None}, None]}

    def test_mixed_mirror_factory(self):
        struct = DeepStruct(MirrorFactory).construct('a.[2].b,c.[2]')
        assert struct == {'a': [{'b': [0, 1], 'c': 'c'}, 1]}

    def test_multi_index(self):
        struct = DeepStruct(list_index=1).construct('[2].a')
        assert struct == [{'a': None}, {'a': None}]
        struct = DeepStruct(MirrorFactory, list_index=1, dict_index=1).construct('a.[2].b,c.[2]')
        assert struct == {'a': [{'b': [0, 1], 'c': [0, 1]}, {'b': [0, 1], 'c': [0, 1]}]}

    def test_multi_branch(self):
        struct = DeepStruct().construct('a,b:1.c', 'd')
        assert struct == {'a': {'c': None}, 'b': {'d': None}}
        struct = DeepStruct().construct('a,b:1.c', '[2].d')
        assert struct == {'a': {'c': None}, 'b': [{'d': None}, None]}


class CycleFactory:
    manu = cycle(('toto', 'titi'))
    slug = cycle(('sw', 'ap'))
    cnt = 0
    @classmethod
    def key(cls, sub):
        if sub == 'manufacturer':
            return next(cls.manu)
        if sub == 'slug':
            return next(cls.slug)
        if sub == 'name':
            val = 'name_' + str(cls.cnt)
            cls.cnt += 1
            return val


class CountingFactory:
    cnt = Counter()
    @classmethod
    def key(cls, sub):
        cnt = cls.cnt[sub]
        cls.cnt[sub] = cnt + 1
        return sub + '_' + str(cnt)


class TestStructExtract:

    def test_simple_extract(self):
        struct = DeepStruct(CycleFactory, list_index=1).construct('results.[2].model.manufacturer')
        assert deep_struct_collect(struct, 'results.#.model', 'manufacturer') == ['toto', 'titi']

    def test_deep_extract(self):
        spec = 'result.locations.[2].children.[2].equipment.[2].model.manufacturer,tags'
        struct = DeepStruct(CycleFactory, list_index=1).construct(spec)
        assert set(deep_struct_collect(struct,
               'result.locations.#.children.#.equipment.#.model', 'manufacturer')) == set(('toto', 'titi'))

    def test_conditional_extract(self):
        spec = 'results.[2].model.tags,manufacturer.[2].slug'
        struct = DeepStruct(CycleFactory, list_index=1).construct(spec)
        assert deep_struct_collect(struct, 'results.#.model',
                                   'manufacturer',
                                   Condition('tags.#.slug', ope.eq, 'ap', any)) == ['toto', 'titi']
        assert deep_struct_collect(struct, 'results.#.model',
                                   'manufacturer',
                                   Condition('tags.#.slug', ope.eq, 'ap', all)) == []
        spec = 'results.[2].model.tags,manufacturer.[1].slug'
        struct = DeepStruct(CycleFactory, list_index=1).construct(spec)
        assert deep_struct_collect(struct, 'results.#.model',
                                   'manufacturer',
                                   Condition('tags.#.slug', ope.eq, 'ap', any)) == ['titi']
        assert deep_struct_collect(struct, 'results.#.model',
                                   'manufacturer',
                                   Condition('tags.#.slug', ope.eq, 'ap', all)) == ['titi']

    def test_conditional_extract_and(self):
        spec = 'results.[2].model.tags,name,manufacturer.[2].slug'
        struct = DeepStruct(CycleFactory, list_index=1).construct(spec)
        data = deep_struct_collect(struct, 'results.#.model',
                                   'name',
                                   Condition('tags.#.slug', ope.eq, 'ap', any) and
                                   Condition('manufacturer', ope.eq, 'titi'))
        assert data == ['name_1']

    def test_multiple_extract(self):
        struct = DeepStruct(CountingFactory, list_index=1).construct('results.[2].model.manu,tags')
        assert deep_struct_collect(struct, 'results.#.model', 'manu,tags') == [('manu_0', 'tags_0'),
                                                                               ('manu_1', 'tags_1')]
