
from collections import defaultdict, Mapping
import json
from functools import partial


def get_accessors_for_object(cls, obj):
    """ return standard object accessors (get, set) if obj is an instance of cls
        else return dict accessors
        useful for dict/django.models.Model dichotomy (before/after object creation)
    """
    return (partial(getattr, obj), partial(setattr, obj)) if isinstance(obj, cls) \
        else (partial(dict.__getitem__, obj), partial(dict.__setitem__, obj))


class SkipMissing(object):
    pass


def extract_translate(map, trans, remove=False, default=SkipMissing):
    """ Extract items from a dict and translate their keys
    :param map: the source dict
    :param trans: the translation dict
    :param remove: if True the fields are removed from map
    :param default: what to do if key_s is missing from map:
                    if 'Exception' then raise, if 'SkipMissing' then skip,
                    else value substituted for the missing key_s (single value or dict)
    :return: the extracted dict
    """
    if default is Exception:
        get = map.pop if remove else map.__getitem__
        return {v: get(k) for k, v in trans.items()}
    if default is SkipMissing:
        get = map.pop if remove else map.__getitem__
        res = {}
        for k, v in trans.items():
            try:
                res[v] = get(k)
            except KeyError:
                pass
        return res
    get = map.pop if remove else map.get
    if isinstance(default, Mapping):
        return {v: get(k, default[k]) for k, v in trans.items()}
    return {v: get(k, default) for k, v in trans.items()}


def extract_dict(map, keys, remove=False, default=SkipMissing):
    """ Extract items from a dict
    :param map: the source dict
    :param keys: the keys iterator
    :param remove: if True the fields are removed from map
    :param default: what to do if key_s is missing from map:
                    if 'Exception' then raise, if 'SkipMissing' then skip,
                    else value substituted for the missing key_s (single value or dict)
    :return: the extracted dict
    """
    if default is Exception:
        get = map.pop if remove else map.__getitem__
        return {k: get(k) for k in keys}
    if default is SkipMissing:
        get = map.pop if remove else map.__getitem__
        res = {}
        for k in keys:
            try:
                res[k] = get(k)
            except KeyError:
                pass
        return res
    get = map.pop if remove else map.get
    if isinstance(default, Mapping):
        return {k: get(k, default.get(k)) for k in keys}
    return {k: get(k, default) for k in keys}


def update_filter(src, dest, keys, force=False):
    """ Copy keys from a source mapping to a destination mapping
    :param src:
    :param dest:
    :param keys: an iterable of keys to copy
    :param force: if True all keys are replaced in dest else,
      only keys existing in source are replaced in dest
    :return: the destination mapping
    """
    if src or force:
        for key in keys:
            if force:
                dest[key] = src.get(key)
            elif key in src:
                dest[key] = src[key]
    return dest


class KeyCounter(object):
    def __init__(self, *args):
        self.data = defaultdict(int)
    def record(self, cont):
        if isinstance(cont, str):
            self.data[cont] += 1
            return
        for k in cont:
            self.data[k] += 1
    def __len__(self):
        if len(self.data):
            return max(v for v in self.data.values())
        return 0
    def __nonzero__(self):
        return bool(self.data)
    def __str__(self):
        return json.dumps(dict(self.data), indent=4)


class MissingRaises:
    pass


class BijectionMapper(dict):
    """ A dictionary class with an attribute-like access and a reverse mapping
        Fails and raises if any key_s or value is duplicated (bijection)
    """

    def __init__(self, *pairs):
        self.pairs = pairs
        dict.__init__(self, pairs)
        if len(self) != len(pairs):
            raise KeyError("Duplicated keys")
        self.backward = dict((v, k) for k, v in pairs)
        if len(self.backward) != len(pairs):
            raise ValueError("Duplicated values")

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    @property
    def reversed_pairs(self):
        return tuple((v, k) for k, v in self.pairs)

    @property
    def for_echoices(self):
        return tuple((k, v, k.lower()) for k, v in self.pairs)

    @property
    def ordered_keys(self):
        return tuple(k for k, v in self.pairs)

    @property
    def ordered_values(self):
        return tuple(v for k, v in self.pairs)

    def from_value(self, value, default=MissingRaises):
        if default is MissingRaises:
            return self.backward[value]
        return self.backward.get(value, default)

    def has_value(self, value):
        return value in self.backward

    def from_value_or_key(self, item):
        """
        returns a key_s from a value
        if not found, check if item is a key_s and returns it unchanged
        :param item: a value or a key_s
        """
        try:
            return self.backward[item]
        except KeyError:
            self[item]
            return item

    def from_key_or_value(self, item):
        """
        returns a value from a key_s
        if not found, check if item is a value and returns it unchanged
        :param item: a key_s or a value
        """
        try:
            return self[item]
        except KeyError:
            self.backward[item]
            return item
