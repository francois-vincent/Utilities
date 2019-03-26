
import operator as ope


def in_(a, b):
    return ope.contains(b, a)


class OrderedSet(set):
    def __init__(self, seq=()):
        super().__init__()
        self.ord = []
        for e in seq:
            self.add(e)

    def add(self, elt):
        if elt not in self:
            set.add(self, elt)
            self.ord.append(elt)

    @property
    def ordered(self):
        return self.ord


class Filter:
    tr_python = {'not': ope.ne, 'in': in_, 'contains': ope.contains,
                 'gt': ope.gt, 'lt': ope.lt, 'gte': ope.ge, 'lte': ope.le, 'eq': ope.eq}
    tr_sql = {'not': '<>%r', 'in': ' IN %r', 'gt': '>%r', 'lt': '<%r', 'gte': '>=%r', 'lte': '<=%r',
              'array_contains': " @> '{%s}'", 'array_in': " <@ '{%s}'"}

    @classmethod
    def translate_py(cls, *args):
        """ translate (key, value) filter to (key, op, value) filter where op is python operator
        :param args: (tuple) (key, value) or (key, op, value)
        :return: (tuple) (key, op, value)
        """
        if len(args) is 3:
            # if (key, op, value), return unchanged
            return args  # pragma nocover
        key, value = args
        if '__' in key:
            key, op = key.split('__')
            return key, cls.tr_python[op], value
        return key, ope.eq, value

    @classmethod
    def translate_sql(cls, key, value):
        """ translate filter with (quasi)django notation to sql notation
        :param key: a key in (quasi)django notation
        :param value: a value to compare
        :return: the equivalent sql expression
        """
        if '__' in key:
            key, op = key.split('__')
            if op != 'in' or len(value) > 1:
                return key + cls.tr_sql[op] % (value,)
            value = value[0]
        return key + '=' + repr(value)


class TableContainer:
    def __init__(self, table, fields):
        """ constructor
        :param table: (list) of fixed length tuples
        :param fields: (tuple) labels of columns in natural order
        """
        self.table = table
        self.fields = fields
        self.idx = {k: i for i, k in enumerate(fields)}  # translates column name to column index
        self.filters = ()

    def __getitem__(self, item):
        return self.table[item]

    def __len__(self):
        return len(self.table)

    @property
    def new(self):
        return TableContainer(self.table, self.fields)

    def filter(self, filters=()):
        if filters:
            table = self.new
            table.filters = filters
            return table
        return self

    def iter_dict(self):
        """ iterate over lines of table rendered as dict {label: value}
        """
        return (dict(zip(self.fields, l)) for l in self.table)

    def iter_filter(self, *filters):
        """ generator over filtered raw lines of the table
        :param filters: iterable of tuple (key, value) or (key, op, value)
        """
        flt = []
        for f in filters:
            if f:
                k, op, v = Filter.translate_py(*f)
                flt.append((self.idx[k], op, v))
        for l in self.table:
            skip = False
            for i, op, v in flt:
                if not op(l[i], v):
                    skip = True
                    break
            if skip:
                continue
            yield l

    def distinct(self, keys, filters=()):
        """ return distinct keys, preserving order
        :param keys: (tuple)
        :param filters: list of filters
        """
        kidx = [self.idx[k] for k in keys]
        d = OrderedSet()
        for l in self.iter_filter(*filters):
            d.add(tuple(l[i] for i in kidx))
        return d

    def aggregate(self, keys, fields, filters=()):
        """ aggregate lines of table
        :param keys: (tuple) aggregate along this set of keys
        :param fields: list of pairs (key, aggregator) where aggregator is a dict-like class
        :param filters: list of filters
        """
        kidx = [self.idx[k] for k in keys]
        fld = [(self.idx[k], v()) for k, v in fields]
        for l in self.iter_filter(*filters):
            key = tuple(l[i] for i in kidx)
            for i, v in fld:
                v[key] = l[i]
        return [v for _, v in fld]


class CountSortMixin:
    def sorted(self, reverse=False):
        return sorted(((k, v) for k, v in self.items()), key=ope.itemgetter(1), reverse=reverse)


class LenSortMixin:
    def sorted(self, reverse=False):
        return sorted(((k, v) for k, v in self.items()), key=lambda x: len(x[1]), reverse=reverse)


class FilteredMixin:
    def __init__(self, op, value):
        dict.__init__(self)
        self.op = Filter.tr_python[op] if isinstance(op, basestring) else op
        self.value = value

    def __call__(self):
        return self


class Count(CountSortMixin, dict):
    def __setitem__(self, key, value):
        if key in self:
            dict.__setitem__(self, key, self[key] + 1)
        else:
            dict.__setitem__(self, key, 1)


class FilteredCount(FilteredMixin, CountSortMixin, dict):
    def __setitem__(self, key, value):
        if self.op(value, self.value):
            if key in self:
                dict.__setitem__(self, key, self[key] + 1)
            else:
                dict.__setitem__(self, key, 1)
        elif key not in self:
            dict.__setitem__(self, key, 0)


class AggList(LenSortMixin, dict):
    def __setitem__(self, key, value):
        if key in self:
            self[key].append(value)
        else:
            dict.__setitem__(self, key, [value])


class AggSet(LenSortMixin, dict):
    def __setitem__(self, key, value):
        if key in self:
            self[key].add(value)
        else:
            dict.__setitem__(self, key, {value})
