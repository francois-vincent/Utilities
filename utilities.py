
from collections import defaultdict, Mapping
import json
from functools import partial


def get_accessors_for_object(cls, obj):
    """ return standard object accessors if obj is an instance of cls
        else return dict accessors
        usefull for dict/django.models.Model dichotomy (before/after object creation)
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
    :param default: what to do if key is missing from map:
                    if 'Exception' then raise, if 'SkipMissing' then skip,
                    else value substituted for the missing key (single value or dict)
    :return: the extracted dict
    """
    if default is Exception:
        get = map.pop if remove else map.__getitem__
        return {v: get(k) for k, v in trans.iteritems()}
    if default is SkipMissing:
        get = map.pop if remove else map.__getitem__
        res = {}
        for k, v in trans.iteritems():
            try:
                res[v] = get(k)
            except KeyError:
                pass
        return res
    get = map.pop if remove else map.get
    if isinstance(default, Mapping):
        return {v: get(k, default[k]) for k, v in trans.iteritems()}
    return {v: get(k, default) for k, v in trans.iteritems()}


def extract_dict(map, keys, remove=False, default=SkipMissing):
    """ Extract items from a dict
    :param map: the source dict
    :param keys: the keys iterator
    :param remove: if True the fields are removed from map
    :param default: what to do if key is missing from map:
                    if 'Exception' then raise, if 'SkipMissing' then skip,
                    else value substituted for the missing key (single value or dict)
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
        if isinstance(cont, basestring):
            self.data[cont] += 1
            return
        for k in cont:
            self.data[k] += 1
    def __len__(self):
        if len(self.data):
            return max(v for v in self.data.itervalues())
        return 0
    def __nonzero__(self):
        return bool(self.data)
    def __str__(self):
        return json.dumps(dict(self.data), indent=4)
