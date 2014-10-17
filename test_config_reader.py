# -*- coding: utf-8 -*-

import mock
import unittest

from config_reader import CachedConfigReader, ini_parser, json_parser, ConfigurationFileError

CachedConfigReader.check_dir = False


yaml_file = \
"""# YAML file
"""

ini_file = \
"""# CONF file
[owner]
name=juan dona
organization=cablage ideal

[database]
server=192.0.2.42     ; use IP address in case network name resolution is not working
port=143
name = "acme payroll.dat"
"""

# JSON files do not accept comments
json_file = \
"""
{
  "menu": {
    "id": 1,
    "value": "File",
    "popup": {
      "menuitems": [
        {"value": "Open", "onclick": "OpenDoc()"},
        {"value": "Close", "onclick": "CloseDoc()"}
      ]
    }
  }
}
"""

xml_file = \
"""# XML file
"""


def mock_open(data):
    class open(object):
        def __init__(self, *args):
            self.lines = [li + '\n' for li in data.split('\n')]
            self.cnt = 0
        def read(self, *args):
            return data
        def readline(self):
            if self.cnt >= len(self.lines):
                return ''
            li = self.lines[self.cnt]
            self.cnt += 1
            return li
        def readlines(self):
            return self.lines
        def next(self):
            li = self.readline()
            if li:
                return li
            raise StopIteration
        def close(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        __next__ = next  # python 3
    return open


def mock_open_error(*args):
    raise IOError


class ConfigReaderTestCase(unittest.TestCase):

    def test_default_parser(self):
        with mock.patch('__builtin__.open', mock_open(ini_file)):
            ccr = CachedConfigReader.get_instance('dummy')
            self.assertEqual(ccr.default_parser, ini_parser)
            conf = ccr.read_config('conf.ini')
            self.assertEqual(conf.get('owner.name'), 'juan dona')

    def test_set_default_parser(self):
        with mock.patch('__builtin__.open', mock_open(json_file)):
            ccr = CachedConfigReader.get_instance('dummy')
            CachedConfigReader.set_default_parser('json')
            self.assertEqual(ccr.default_parser, json_parser)
            conf = ccr.read_config('conf.json')
            self.assertEqual(conf.get('menu.value'), 'File')
            CachedConfigReader.set_default_parser('ini')

    def test_cached_instance(self):
        with mock.patch('__builtin__.open', mock_open(ini_file)):
            ccr = CachedConfigReader.get_instance('dummy')
            conf = ccr.read_config('conf4.ini')
            self.assertEqual(conf.get('owner.name'), 'juan dona')
            ccr2 = CachedConfigReader.get_instance('dummy')
            conf2 = ccr2.read_config('conf4.ini', 'random_parser')    # parser is ignored
            self.assertIs(ccr, ccr2)
            self.assertIs(conf, conf2)

    def test_wrong_folder_raise(self):
        CachedConfigReader.check_dir = True
        try:
            self.assertRaises(IOError, CachedConfigReader.get_instance, '/doesnotexists')
        finally:
            CachedConfigReader.check_dir = False

    def test_wrong_file_noraise(self):
        with mock.patch('__builtin__.open', mock_open_error):
            ccr = CachedConfigReader.get_instance('dummy')
            conf = ccr.read_config('conf2.ini')
            self.assertEqual(dict(conf), {})

    def test_wrong_file_raise(self):
        with mock.patch('__builtin__.open', mock_open_error):
            ccr = CachedConfigReader.get_instance('dummy')
            self.assertRaises(ConfigurationFileError, ccr.read_config, 'conf3.ini', None, '__raise__')

    def test_wrong_parser_noraise(self):
        pass

    def test_wrong_parser_raise(self):
        pass

    def test_ini_parser(self):
        pass

    def test_json_parser(self):
        with mock.patch('__builtin__.open', mock_open(json_file)):
            ccr = CachedConfigReader.get_instance('dummy')
            conf = ccr.read_config('conf.json', 'json')     # override default parser
            self.assertEqual(conf.get('menu.value'), 'File')
            self.assertEqual(conf.get('menu.id'), 1)

    def test_yaml_parser(self):
        pass

    def test_xml_parser(self):
        pass

    def test_guess_parser_from_extension(self):
        pass

    def test_guess_parser_from_comment(self):
        pass

    def test_guess_parser_from_content(self):
        pass

    def test_simple_keys(self):
        pass

    def test_numerical_keys(self):
        pass

    def test_boolean_keys(self):
        pass

    def test_list_keys(self):
        pass

    def test_date_keys(self):
        pass

    def test_override_keys(self):
        pass

    def test_add_parser(self):
        pass


if __name__ == '__main__':
    unittest.main()
