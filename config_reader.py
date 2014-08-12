# -*- coding: utf-8 -*-

import ConfigParser
import json
import os
import yaml


class Config(dict):
    """
    A Config is a subclass of dict whose values are strings or recursively dict whose values are strings or ...
    Keys are strings, and can be expressed as chains of keys separated by dots,
    eg c['section.subsection.element'] is equivalent to c['section']['subsection']['element'].
    You can write c['section.subsection']['element'] but you can't write c['section']['subsection.element']
    as c['section'] is a dict, not a Config. You must write Config(c['section'])['subsection.element'].
    Non leaf elements are always dict, only leaf elements can be lists.
    """
    _boolean_states = ConfigParser.RawConfigParser._boolean_states

    def __getitem__(self, key):
        r = self
        for k in key.split('.'):
            r = dict.__getitem__(r, k)
        return r

    def get(self, k, d=None):
        try:
            return self[k]
        except KeyError:
            return d

    def get_int(self, k, d=0):
        try:
            return int(self.get(k, d))
        except TypeError:
            raise ValueError('Not a leaf or not an integer: %s' % k)

    def get_float(self, k, d=0.0):
        try:
            return float(self.get(k, d))
        except TypeError:
            raise ValueError('Not a leaf or not a float: %s' % k)

    def get_boolean(self, k, d='0'):
        try:
            v = self.get(k, d).lower()
        except AttributeError:
            raise KeyError('Not a leaf or not a boolean: %s' % k)
        if v not in self._boolean_states:
            raise ValueError('Not a boolean %s: %s' % (k, v))
        return self._boolean_states[v]
    get_bool = get_boolean

    def get_json(self, k, d='[]'):
        """ only used to get a list from an ini config file
            use syntax: ["a","b"] (double quotes mandatory)
        """
        return json.loads(self.get(k, d))


def yaml_parser(file):
    with open(file, 'r') as f:
        return Config(yaml.safe_load(f))


def ini_parser(file):
    # don't need OrderedDict
    cp = ConfigParser.RawConfigParser(dict_type=dict)
    with open(file, 'r') as f:
        cp._read(f, file)
    # remove some stuff
    for s in cp._sections.itervalues():
        del s['__name__']
    return Config(cp._sections)


def json_parser(file):
    with open(file, 'r') as f:
        return Config(json.loads(f))

parsers = dict(
    yaml=yaml_parser,
    ini=ini_parser,
    conf=ini_parser,
    json=json_parser
)


class CachedConfigReader(object):
    """
    Implements configuration reading with features:
    - configurable parser:
      use specified or default parser or parser specific to file extension,
      or use parser defined in first comment line of config file.
    - two levels instance caching:
      CachedConfigReader.get_config_reader(dir) returns a config reader instance for the specified directory.
      read_config(config_file) reads and cache the specified config file as a mapping object.
    """
    dir_cache = {}

    def __init__(self, config_dir, parser):
        self.config_dir = config_dir
        self.parser = parser
        self.cache = {}

    @classmethod
    def get_config_reader(cls, config_dir, parser=yaml_parser):
        path = os.path.abspath(config_dir)
        if path not in cls.dir_cache:
            cls.dir_cache[path] = CachedConfigReader(path, parser)
        return cls.dir_cache[path]

    def read_config(self, config, parser=None):
        if config not in self.cache:
            if parser is None:
                parser = self.parser
            path = os.path.join(self.config_dir, config)
            try:
                parser = parsers[config.rsplit('.', 1)[1]]
            except (KeyError, IndexError):
                with open(path, 'r') as f:
                    first_line = f.readline()
                if first_line.startswith('#'):
                    for k, v in parsers:
                        if k in first_line.lower():
                            parser = v
                            break
            self.cache[config] = parser(path)
        return self.cache[config]

    def reload(self, config=None):
        if config:
            del self.cache[config]
        else:
            self.cache = {}
    reset = clear = reload
