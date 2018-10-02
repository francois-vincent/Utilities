import functools
from django.db import models

from .utilities import  make_id_with_prefix


class UIDField(models.Field):
    """ A auto fill UIDField that renders as a simple CharField,
        with 36**12 >4e18 combinations
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 12)
        kwargs.setdefault('default', functools.partial(make_id_with_prefix, length=kwargs['max_length']))
        kwargs.setdefault('unique', True)
        super(UIDField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(UIDField, self).deconstruct()
        return name, 'models.CharField', args, kwargs
