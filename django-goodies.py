import functools
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


def custom_sql(sql, *args):
    with connection.cursor() as cursor:
        cursor.execute(sql, args)
        return cursor.fetchall()


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
