import functools

from django.core.exceptions import ValidationError
from django.db import connection, models

from .utilities import make_id_with_prefix


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


class ListCharField(models.CharField):
    """ Auto truncating CharField that drops on the left side
    """

    def __init__(self, sep=':', **kwargs):
        self.sep = sep
        kwargs['default'] = ''
        super().__init__(**kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value and len(value) > self.max_length:
            index = value.find(self.sep, len(value) - self.max_length)
            if index > -1:
                return value[index+1:]
            raise ValidationError("max length exceeded", code='max_length')
        return value


def custom_sql(sql, *args):
    with connection.cursor() as cursor:
        cursor.execute(sql, args)
        return cursor.fetchall()


def make_condition(field, value_s, coord='AND'):
    """ build a WHERE sql condition in the general form:
        < COORD field IN (value_s)> if value_s is a sequence
        < COORD field=value_s> if value_s is a single value (string, integer or boolean)
    :param field: field name
    :param value_s: a single value or a sequence
    :param coord: 'AND', 'OR' or None
    :return: (string) empty if value_s is None or an empty sequence
    """
    def prep_coord(cond, coord):
        if coord:
            return ' ' + coord + ' ' + cond
        return cond

    if not value_s and value_s not in (0, False):
        return ''
    if isinstance(value_s, (tuple, list, set)):
        if not isinstance(value_s, tuple):
            value_s = tuple(value_s)
        if len(value_s) == 1:
            value_s = value_s[0]
        else:
            return prep_coord("%s IN %s" % (field, value_s), coord)
    return prep_coord("%s=%r" % (field, value_s), coord)


def quote(param):
    try:
        return int(param)
    except ValueError:
        return "'" + param + "'"


def translate_filter(key, value):
    operators = {'in': ' IN ', 'like': ' LIKE ', 'gt': '>', 'lt': '<', 'gte': '>=', 'lte': '<='}
    if '__' in key:
        key, op = key.split('__')
        return key + operators[op] + quote(value)
    return key + '=' + quote(value)


def get_table(table_name, fields, filters, order_by=None, debug=False):
    """ Get a table's fields via raw sql request
    :param table_name: true table name in db (ie {app}_{model} lower case)
    :param fields: ordered list of fields to retrieve from table
    :param filters: iterable of pairs (field, value)
    :param order_by: a single field to set an order on, if prefixed with '-', order is decreasing
    :return: a list of tuples
    """
    assert len(fields) > 0
    sql_fields = ', '.join('t.' + f for f in fields)
    sql_filter = ' WHERE ' + ' AND '.join('t.' + translate_filter(k, v) for k, v in filters) if filters else ''
    if order_by:
        if order_by[0] == '-':
            direction = ' DESC'
            order_by = order_by[1:]
        else:
            direction = ' ASC'
        sql_order_by = ' ORDER BY t.' + order_by + direction
    else:
        sql_order_by = ''
    sql = "SELECT {} FROM {} t{}{}".format(sql_fields, table_name, sql_filter, sql_order_by)
    return sql if debug else custom_sql(sql)
