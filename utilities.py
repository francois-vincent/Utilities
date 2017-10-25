
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


def extract_translate(map, trans, remove=False, default=None):
    """ extract items from a dict and translate their keys
    :param map: the source dict
    :param trans: the translation dict
    :param remove: if True the field is removed from map
    :param default: if Exception and the field is missing from map then raise,
                    if SkipMissing and the field is missing from map then skip,
                    else missing field is None
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
    if remove:
        return {v: map.pop(k, default) for k, v in trans.iteritems()}
    else:
        return {v: map.get(k, default) for k, v in trans.iteritems()}


def extract_dict(map, keys, remove=False, default=None):
    """ extract items from a dict
    :param map: the source dict
    :param keys: the keys iterator
    :param remove: if True the field is removed from map
    :param default: if Exception and the field is missing from map then raise,
                    if SkipMissing and the field is missing from map then skip,
                    else missing field is None
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
    if remove:
        return {k: map.pop(k, default) for k in keys}
    else:
        return {k: map.get(k, default) for k in keys}
