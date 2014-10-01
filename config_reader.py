# -*- coding: utf-8 -*-

# TODO
# use special keyword to guess parser from file
# faire des tests
# add a date type with tz in Config

import copy
import functools
import os

# parser modules
try:
    import simplejson as json
except ImportError:
    import json

import ConfigParser

try:
    import yaml
except ImportError:
    class yaml(object):
        @staticmethod
        def safe_load(f):
            raise RuntimeError("YAML configuration file requires PyYAML parser (pip install pyyaml)")

try:
    import xmltodict
except ImportError:
    class xmltodict(object):
        @staticmethod
        def parse(f):
            raise RuntimeError("XML configuration file requires xmltodict parser (pip install xmltodict)")


# predefined parser functions
# a parser function accepts a config file full path as unique parameter and returns a Config instance

def json_parser(file):
    with open(file, 'r') as f:
        return Config(json.load(f))


def ini_parser(file):
    # don't need OrderedDict
    cp = ConfigParser.RawConfigParser(dict_type=dict)
    with open(file, 'r') as f:
        cp._read(f, file)
    # remove some stuff
    for s in cp._sections.itervalues():
        del s['__name__']
    return Config(cp._sections)


def yaml_parser(file):
    with open(file, 'r') as f:
        return Config(yaml.safe_load(f))


def xml_parser(file):
    with open(file, 'r') as f:
        return Config(xmltodict.parse(f.read()))


class ConfigurationError(RuntimeError):
    pass


class ConfigurationFileError(ConfigurationError):
    pass


class ConfigurationKeyError(ConfigurationError):
    pass


class ConfigurationValueError(ConfigurationError):
    pass


class Config(dict):
    """
    A Config is a subclass of dict whose values are simple python objects (strings, integers, booleans or floats),
    or lists, or recursively dicts whose values are simple python objects or lists, or ...
    This rule apply to Yaml formatted files too: non leaf elements are always dicts, only leaf elements can be lists.
    Keys are strings, and can be expressed as chains of keys separated by dots,
    eg c.get('section.subsection.option') is roughly the same as c.get('section').get('subsection').get('option')
    salted with appropriate exception handling and default value management.
    """
    _boolean_states = {'yes': True, 'true': True, 'on': True, '1': True,
                       'no': False, 'false': False, 'off': False, '0': False}

    @classmethod
    def add_bool_literals(cls, true, false):
        cls._boolean_states[true] = True
        cls._boolean_states[false] = False

    def _deepcopy(self):
        return copy.deepcopy(self)

    def _update(self, other):
        for key, value in other.iteritems():
            r = self
            chain = key.split('__')
            for k in chain[:-1]:
                try:
                    r = dict.__getitem__(r, k)
                except KeyError:
                    r[k] = {}
                    r = r[k]
            if value is None:
                try:
                    del r[chain[-1]]
                except KeyError:
                    pass
            else:
                r[chain[-1]] = value
        return self

    def override_config(self, **kwargs):
        """ returns an object that is a decorator as well as a context manager.
            compound keys are expressed with double underscore notation,
            ie 'section.subsection.option' is written 'section__subsection__option'.
            you can specify a value=None to delete any chained key if it exists.
            usage as context manager:
            with c.override_config(section__subsection__option=value):
                ...
            usage as decorator:
            @c.override_config(section__subsection__option=value)
            def function_or_method(*args, **kwargs):
                ...
        """
        this = self
        class ContextDecorator(object):
            def __init__(self, **kwargs):
                self.overrides = kwargs
            def __enter__(self):
                self.copy = this._deepcopy()
                return this._update(self.overrides)
            def __exit__(self, *args):
                this.clear()
                this.update(self.copy)
            def __call__(self, f):
                @functools.wraps(f)
                def decorated(*args, **kwds):
                    with self:
                        return f(*args, **kwds)
                return decorated
        return ContextDecorator(**kwargs)

    def __getitem__(self, key):
        """ general access operator (leaf and non leaf), can raise exception
        """
        r = self
        try:
            for k in key.split('.'):
                r = dict.__getitem__(r, k)
        except KeyError as e:
            raise ConfigurationKeyError("%s in '%s'" % (e, key))
        return r

    def get(self, k, d=None):
        """ general access operator (leaf and non leaf), always returns default if key anavailable
        """
        try:
            return self[k]
        except ConfigurationKeyError:
            return d

    def get_leaf(self, k, d=None):
        """ general leaf access operator (no typecheck), raises or returns default if key unavailable
        """
        try:
            return self[k]
        except ConfigurationKeyError:
            if d == '__raise__':
                raise
            return d

    def _default_or_raises(self, key, kind, d):
        if d == '__raise__':
            raise ConfigurationValueError('Not a leaf or not a %s: %s' % (kind, key))
        return d

    def get_string(self, k, d=''):
        """ leaf string access operator, raises or returns default if key unavailable or not a string
        """
        v = self.get_leaf(k, d)
        if isinstance(v, basestring):
            return v
        return self._default_or_raises(k, 'string', d)

    def get_integer(self, k, d=0):
        """ leaf integer access operator, raises or returns default if key unavailable or not an integer
        """
        v = self.get_leaf(k, d)
        try:
            return int(v)
        except TypeError:
            return self._default_or_raises(k, 'integer', d)
    get_int = get_integer

    def get_float(self, k, d=0.0):
        """ leaf float access operator, raises or returns default if key unavailable or not a float
        """
        v = self.get_leaf(k, d)
        try:
            return float(v)
        except TypeError:
            return self._default_or_raises(k, 'float', d)

    def get_boolean(self, k, d=False):
        """ leaf boolean access operator, raises or returns default if key unavailable or not a boolean
        """
        v = self.get_leaf(k, d)
        if isinstance(v, bool):
            return v
        if v in (0, 1):
            return bool(v)
        try:
            return self._boolean_states[v.lower()]
        except (KeyError, AttributeError):
            return self._default_or_raises(k, 'boolean', d)
    get_bool = get_boolean

    def get_list(self, k, d=None):
        """ leaf list access operator, raises or returns default if key unavailable or not a list.
            ini config files must use syntax: ["a","b"] (double quotes mandatory)
        """
        d = d if d else []
        v = self.get_leaf(k, d)
        if isinstance(v, list):
            return v
        try:
            v = json.loads(v)
        except (ValueError, TypeError):
            v = None
        if isinstance(v, list):
            return v
        return self._default_or_raises(k, 'list', d)


class CachedConfigReader(object):
    """
    Implements configuration reading with features:
    - configurable parser. By order of priority:
      1- explicitly specified in read_config(),
      2- use file extension,
      3- specified in first comment line of config file,
      4- instance default parser,
      5- class default parser
    - two levels instance caching:
      CachedConfigReader.get_instance(dir) returns a config reader instance for the specified directory,
      (one directory == one instance).
      cr.read_config(config_file) reads and cache the specified config file as a mapping object.
    """
    parsers_dict = dict(
        yaml=yaml_parser,
        yml=yaml_parser,
        ini=ini_parser,
        conf=ini_parser,
        json=json_parser,
        xml=xml_parser,
    )
    dir_cache = {}
    default_parser = yaml_parser

    def __init__(self, config_dir, parser):
        self.config_dir = config_dir
        self.default_parser = self.get_parser(parser)
        self.cache = {}

    @classmethod
    def add_parser(cls, name, parser):
        CachedConfigReader.parsers_dict[name] = parser

    @classmethod
    def get_instance(cls, config_dir, parser=None):
        path = os.path.abspath(config_dir)
        if path not in cls.dir_cache:
            cls.dir_cache[path] = CachedConfigReader(path, parser)
        return cls.dir_cache[path]

    def get_parser(self, parser):
        if parser is None:
            return self.default_parser
        if isinstance(parser, basestring):
            return CachedConfigReader.parsers_dict[parser]
        return parser

    def get_parser_from_file(self, path):
        parser = self.default_parser
        try:
            # try to get parser from file extension
            parser = CachedConfigReader.parsers_dict[path.rsplit('.', 1)[1]]
        except (KeyError, IndexError):
            # else try to guess parser from first comment line
            with open(path, 'r') as f:
                first_line = f.readline().lower()
            if first_line.startswith('#'):
                for k, v in CachedConfigReader.parsers_dict.iteritems():
                    if k in first_line:
                        parser = v
                        break
        return parser

    def instanciate_config(self, name, config):
        self.cache[name] = config

    def read_config(self, config_name, parser=None, default={}):
        """ reads and parse the config file, or get the cached configuration if available.
            you can specify default='__raise__' to raise an exception on missing file
        """
        if config_name not in self.cache:
            path = os.path.join(self.config_dir, config_name)
            try:
                if parser:
                    parser = self.get_parser(parser)
                else:
                    parser = self.get_parser_from_file(path)
                self.instanciate_config(config_name, parser(path))
            except IOError:
                if default == '__raise__':
                    raise ConfigurationFileError("Configuration file not found: %s", path)
                self.instanciate_config(config_name, Config(default))
        return self.cache[config_name]
    get_config = read_config

    def reload(self, config=None):
        if config:
            del self.cache[config]
        else:
            self.cache = {}
    reset = clean = clear = reload
