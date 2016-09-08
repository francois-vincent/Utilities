# encoding: utf-8

import re


def run_sequence(self, *args):
    """ run a sequence of methods with optional parameters from an object
    :param self: an object
    :param args: a sequence of:
       - string: call string()
       - tuple or list of:
          - (string, object): call string(object)
          - (string, tuple): call string(*tuple)
          - (string, tuple, dict): call string(*tuple, **dict)
    """
    for i, arg in enumerate(args):
        if isinstance(arg, basestring):
            getattr(self, arg)()
        elif len(arg) is 2:
            param = arg[1]
            if isinstance(param, tuple):
                getattr(self, arg[0])(*param)
            else:
                getattr(self, arg[0])(param)
        elif len(arg) is 3:
            getattr(self, arg[0])(*(arg[1]), **(arg[2]))
        else:
            raise RuntimeError('Bad argument at position {}: {}'.format(i, arg))
    return self


def collapse_op(op):
    """ Decorator to automatically execute a method on a specific host or all platform hosts,
        collecting return values in a dict or a list, or just testing them.
        The decorated method must have its first argument a host specifier (string).
        Usage: if the wrapper method is called with host='host' parameter, the wrapped
        method will be called once with this host.
        If the wrapper method is called with no host= parameter, the wrapped method will
        be called once per host of the platform. The wrapped method will then return a
        value depending of the op parameter.
        :param op:
        - dict:  a dictionary {host: value, ...} of the return values for each host.
        - extend or append: a concatenated list of return values, use 'extend' if
          the wrapped method returns a sequence, otherwise use 'append'.
        - and: a boolean, execution on multiple hosts stops as soon as the wrapped
          method returns False (good to check path or process exists on all hosts).
        - any: a boolean, execution on multiple hosts stops as soon as the wrapped
          method returns True (good to check missing path or process on all hosts).
    """
    op_values = ('dict', 'extend', 'append', 'and', 'any')
    if op not in op_values:
        raise ValueError("Parameter op must be one of {}".format(op_values))
    def wrapper(meth):
        def wrapped(self, *args, **kwargs):
            host = kwargs.pop('host', None)
            if host:
                return meth(self, host, *args, **kwargs)
            elif op == 'dict':
                return {host: meth(self, host, *args, **kwargs) for host in self.hosts}
            elif op in ('extend', 'append'):
                ret = []
                for host in self.hosts:
                    getattr(ret, op)(meth(self, host, *args, **kwargs))
                return ret
            elif op == 'and':
                return all(meth(self, host, *args, **kwargs) for host in self.hosts)
            elif op == 'any':
                return any(meth(self, host, *args, **kwargs) for host in self.hosts)
        return wrapped
    return wrapper


def collapse_self(meth):
    """ Like collapse_op, except that it always returns self
    """
    def wrapper(self, *args, **kwargs):
        host = kwargs.pop('host', None)
        if host:
            meth(self, host, *args, **kwargs)
        else:
            for host in self.hosts:
                meth(self, host, *args, **kwargs)
        return self
    return wrapper


def set_method(cls, func, name=None, deco=None):
    setattr(cls, func.__name__ if name is None else name, func if deco is None else deco(func))


def set_methods_from_conf(cls, conf):
    regex = re.compile(r".*?\[deco:([_A-Za-z0-9()'\"]+)\]")
    for k, v in conf.items():
        if hasattr(v, '__call__'):
            deco = None
            if getattr(v, '__doc__', None):
                deco_spec = regex.findall(v.__doc__)
                if deco_spec:
                    deco = deco_spec[0]
            deco = deco or getattr(cls, 'default_deco', None)
            set_method(cls, v, k, eval(deco) if deco else None)
