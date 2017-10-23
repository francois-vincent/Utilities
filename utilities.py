

def get_accessors_for_object(cls, obj):
    """ return standard object accessors if obj is an instance of cls
        else return dict accessors
        usefull for dict/django.models.Model dichotomy (before/after object creation)
    """
    return (getattr, setattr) if isinstance(obj, cls) else (dict.get, dict.__setitem__)


def extract_translate(map, trans):
    """ extract fields from a dict and translate them
    :param map: the source dict
    :param trans: the translation dict
    :return: the extracted dict
    """
    return {v: map[k] for k, v in trans.iteritems()}
