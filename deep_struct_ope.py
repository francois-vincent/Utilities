
###################
#
#   EXTRACTORS
#
###################


def get_head_tail(path):
    try:
        head, tail = path.split('.', 1)
    except ValueError:
        head, tail = path, None
    return head, tail


class Condition:

    def __init__(self, path, ope, val, meta=None):
        self.path = path
        self.ope = ope
        self.val = val
        self.meta = meta  # builtin any or all
        self.chain_or, self.chain_and = None, None

    def __or__(self, other):
        self.chain_or = other

    def __and__(self, other):
        self.chain_and = other

    def __call__(self, s):
        if self.meta:
            val = self.meta(self.ope(x, self.val) for x in deep_struct_iter(s, self.path))
        else:
            val = self.ope(next(deep_struct_get(s, self.path)), self.val)
        if self.chain_and and val:
            return self.chain_and(s)
        if self.chain_or and not val:
            return self.chain_or(s)
        return val


def deep_struct_get(s, path):
    if not path:
        yield s
        return
    head, tail = get_head_tail(path)
    if head == '#':
        raise ValueError("'#' not allowed in deep_struct_get")
    elif head.isdigit():
        assert isinstance(s, list)
        yield from deep_struct_get(s[int(head)], tail)
    else:
        assert isinstance(s, dict)
        yield from deep_struct_get(s[head], tail)


def deep_struct_iter(s, path):
    try:
        head, tail = path.split('.', 1)
        call = deep_struct_iter
    except ValueError:
        head, tail = path, None
        call = deep_struct_get
    if head == '#':
        assert isinstance(s, list)
        for elt in s:
            yield from call(elt, tail)
    elif head.isdigit():
        assert isinstance(s, list)
        yield from call(s[int(head)], tail)
    else:
        assert isinstance(s, dict)
        yield from call(s[head], tail)


def deep_struct_collect(s, path, key, cond=None):
    """ extract data from a deeply nested structure (dict/list)
    :param s: a nested dict/list structure
    :param path: a dotted notation path in the structure (eg key.index.key.#.key)
           where key is a dict key, index is a list index (integer), and # stands for list iterator
    :param key: the key to extract
    :param cond: the (optional) condition to extract the key: instance of Condition
    :return: a list of extracted data
    """
    result = []
    for sub in deep_struct_iter(s, path):
        if cond(sub) if cond else True:
            result.append(next(deep_struct_get(sub, key)))
    return result


###################
#
#   CONSTRUCTORS
#
###################

class ConstFactory:
    const = None
    @classmethod
    def key(cls, sub):
        return cls.const
    index = key


class MirrorFactory:
    @staticmethod
    def key(sub):
        return sub
    index = key


def get_subscript(sub):
    if sub.startswith('['):
        return int(sub[1:-1]), int
    return sub, str


def get_branch(sub, pos, branches):
    try:
        sub, index = sub.split(':', 1)
    except ValueError:
        return sub, None
    if not pos:
        raise ValueError("Can't set branch on main branch")
    index = int(index) - 1
    if index < 0:
        raise ValueError("branch index must be >0")
    return sub, branches[index]


class DeepStruct:

    def __init__(self, factory=ConstFactory, list_index=0, dict_index=0):
        self.factory = factory
        self.list_index = list_index
        self.dict_index = dict_index

    def construct(self, spec, *branches):
        """ build a recursive struct (dict/list) from a spec
        :param spec: (str) a dotted notation specification of the struct, eg key.[n].key.[m].key,key
        :param branches: a tuple of sub-structure specifications for sub branches

        self.factory: a class that maps key or index to a value
        self.list_index: (integer) if index is greater, element is filled with factory,
          otherwise it is filled with recursive call to construct
        self.list_key: (integer) if enumerate index is greater, element is filled with factory,
          otherwise it is filled with recursive call to construct
        """
        head, tail = get_head_tail(spec)
        subs, typ = get_subscript(head)
        if typ is int:
            return [self.construct(tail) if (tail and i <= self.list_index) else self.factory.index(i)
                    for i in range(subs)]
        else:
            val = {}
            for i, sub in enumerate(subs.split(',')):
                sub, br = get_branch(sub, i, branches)
                if br:
                    val[sub] = self.construct(br)
                elif tail and i <= self.dict_index:
                    val[sub] = self.construct(tail)
                else:
                    val[sub] = self.factory.key(sub)
            return val
