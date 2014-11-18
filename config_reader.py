# -*- coding: utf-8 -*-
__version__ = '0.0.1'

# TODO
# test with nose
# add a date type with tz in Config
# add some logging

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
# a parser function accepts a config file full path as unique parameter and returns a dict

def json_parser(file):
    with open(file, 'r') as f:
        return json.load(f)


def ini_parser(file):
    # don't need OrderedDict
    cp = ConfigParser.RawConfigParser(dict_type=dict)
    with open(file, 'r') as f:
        cp._read(f, file)
        # remove some stuff
    for s in cp._sections.itervalues():
        del s['__name__']
    return cp._sections


def yaml_parser(file):
    with open(file, 'r') as f:
        return yaml.safe_load(f)


def xml_parser(file):
    with open(file, 'r') as f:
        return xmltodict.parse(f.read())


class ConfigurationError(RuntimeError):
    pass


class ConfigurationParserError(ConfigurationError):
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
        """ mostly used by override_config
            parameter is a dictionary with double undescored keys
        """
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
            you can specify a value as None to delete any chained key if it exists.
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

    def get_date(self, k, d=None):
        """ leaf date acces operator, reads an ISO formated naive or tzed date
        """
        pass


class ParserResolver(object):
    parsers_dict = dict(
        ini=ini_parser,
        yaml=yaml_parser,
        json=json_parser,
        xml=xml_parser,
    )
    parsers_aliases = dict(
        ini='ini',
        conf='ini',
        yaml='yaml',
        yml='yaml',
        json='json',
        xml='xml',
    )
    parser_resolution_order = ['ini', 'json', 'yaml', 'xml']

    @classmethod
    def add_parser(cls, name, parser, aliases=(), index=0):
        cls.parsers_dict[name] = parser
        for a in aliases:
            cls.parsers_aliases[a] = name
        if index < 0:
            # poor list.insert() negative index management... it cannot append !
            if index == -1:
                return cls.parser_resolution_order.append(name)
            else:
                index += 1
        cls.parser_resolution_order.insert(index, name)

    def read_config_from_file(self, parser, path):
        if isinstance(parser, basestring):
            parser = self.parsers_dict[parser]
        try:
            conf = Config(parser(path))
            return conf
        except IOError:
            raise
        except Exception as e:
            # Fixme add logging here
            pass

    def get_config_from_file(self, parser, path):
        self.parser_resolution_order = list(self.parser_resolution_order)
        try:
            # try to guess parser from file extension
            parser = self.parsers_aliases[path.rsplit('.', 1)[1]]
        except (KeyError, IndexError):
            config = None
        else:
            self.parser_resolution_order.remove(parser)
            config = self.read_config_from_file(parser, path)
        if config is None:
            # try to guess parser from first line comment
            with open(path, 'r') as f:
                first_line = f.readline().lower()
            if first_line[0] in ('#', ';'):
                for k, v in self.parsers_aliases.iteritems():
                    if k in first_line and v in self.parser_resolution_order:
                        self.parser_resolution_order.remove(v)
                        config = self.read_config_from_file(v, path)
                        break
        if config is None and parser == 'guess_hard':
            # try each remaning parser in order
            for p in self.parser_resolution_order:
                try:
                    config = self.read_config_from_file(p, path)
                except Exception:
                    pass
        if config is None:
            raise ConfigurationFileError("No parser found for file %s" % path)
        return config

    def get_config(self, parser, path):
        """
        méthode de recherche du parser :
        si parser est uclsne fonction:
          lire la config
        si échec
          raise ConfigurationFileError
        si parser est une chaine
          si dans le dico, lire la config,
          si décodage avec le parser échoue, c'est pas 'guess' donc ConfigurationFileError
        si pas dans le dico et pas 'guess'
          raise ConfigurationParserError
        si parser.startswith('guess')
          si extension pas dans la liste, échec
          si décodage avec extension échoue, échec
        si échec et parser.startswith('guess')
          si comment pas dans la liste, échec
          si décodage avec comment échoue, échec
        si échec et parser == 'guess_hard'
          liste des parsers = liste complète - set(extension, comment)
          pour chaque parser de la liste, tenter la lecture
        si échec
          raise ConfigurationFileError
        """
        if isinstance(parser, basestring):
            if parser.startswith('guess'):
                try:
                    return self.get_config_from_file(parser, path)
                except IOError:
                    raise ConfigurationFileError("Could not read file %s" % path)
            else:
                try:
                    parser = self.parsers_aliases[parser]
                except KeyError:
                    raise ConfigurationParserError("Parser %s not found" % parser)
        try:
            config = self.read_config_from_file(parser, path)
        except IOError:
            raise ConfigurationFileError("Could not read file %s" % path)
        if config is None:
            raise ConfigurationFileError(
                "Could not read configuration file %s with parser %s", (path, parser.__name__))
        return config


class CachedConfigReader(object):
    # Fixme
    """
    Implements configuration reading with features:
    - configurable parser. By order of priority:
      1- explicitly specified in read_config(),
      2- use file extension,
      3- specified in first comment line of config file,
      4- class default parser
    - two levels instance caching:
      CachedConfigReader.get_instance(dir) returns a config reader instance for the specified directory,
      (one directory == one instance).
      cr.read_config(config_file) reads and cache the specified config file as a Config object.
    """
    dir_cache = {}
    check_dir = True  # used by test suite
    default_parser = 'guess'
    default_config = None

    def __init__(self, config_dir, parser, default):
        self.config_dir = config_dir
        self.default_parser, self.default_config = parser, default
        self.cache = {}

    add_parser = ParserResolver.add_parser

    @staticmethod
    def first_not_none(*args):
        for arg in args:
            if arg is not None:
                return arg

    @staticmethod
    def all_none(*args):
        return all(arg is None for arg in args)

    @classmethod
    def set_default_parser(cls, parser):
        cls.default_parser = parser
        return cls

    @classmethod
    def reload_all(cls):
        cls.dir_cache = {}
        return cls

    @classmethod
    def get_instance(cls, config_dir, parser=None, default=None):
        path = os.path.abspath(config_dir)
        if path not in cls.dir_cache:
            if cls.check_dir and CachedConfigReader.all_none(default, cls.default_config):
                if not os.access(path, os.R_OK):
                    raise IOError("%s: folder missing or read access forbidden" % path)
            cls.dir_cache[path] = CachedConfigReader(path, parser, default)
        return cls.dir_cache[path]

    def read_config(self, config_name, parser=None, default=None):
        """ reads and parse the config file, or get the cached configuration if available.
            you can specify default=dict(...) to return a default config on missing file or wrong parser
        """
        if config_name not in self.cache:
            path = os.path.join(self.config_dir, config_name)
            try:
                parser = parser or self.default_parser or self.__class__.default_parser
                if parser is None:
                    raise ConfigurationParserError("No parser specified for file: %s" % path)
                config = ParserResolver().get_config(parser, path)
            except Exception:
                default = CachedConfigReader.first_not_none(default, self.default_config, self.__class__.default_config)
                if default is None:
                    raise
                config = Config(default)
            self.cache[config_name] = config
        return self.cache[config_name]

    get_config = read_config

    def reload(self, config=None):
        if config:
            del self.cache[config]
        else:
            self.cache = {}
        return self

    reset = clean = clear = reload
