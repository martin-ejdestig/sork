# This file is part of Sork.
#
# Copyright (C) 2017 Martin Ejdestig <marejde@gmail.com>
#
# Sork is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sork is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sork. If not, see <http://www.gnu.org/licenses/>.

import tempfile
import unittest

from .. import config
from .. import error


_TEST_CONFIG_DEFAULT = {
    'string1': 'abc',
    'integer1': 123,
    'string_array1': ['def', 'ghi'],
    'object1': {
        'string2': 'jkl',
        'integer2': 456
    }
}

_TEST_CONFIG_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'string1': {'type': 'string'},
        'integer1': {'type': 'integer'},
        'string_array1': {'type': 'array', 'items': {'type': 'string'}},
        'object1': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'string2': {'type': 'string'},
                'integer2': {'type': 'integer'}
            }
        }
    }
}


def _test_config_create(path: str) -> config.Config:
    return config.create(path, _TEST_CONFIG_DEFAULT, _TEST_CONFIG_SCHEMA)


def _test_config_from_content(content: str) -> config.Config:
    with tempfile.NamedTemporaryFile(mode='wt') as file:
        file.write(content)
        file.flush()
        return _test_config_create(file.name)


class TestConfig(unittest.TestCase):
    def test_does_not_exist(self):
        cfg = _test_config_create('does_not_exist')
        self.assertEqual(cfg['string1'], 'abc')
        self.assertEqual(cfg['integer1'], 123)
        self.assertEqual(cfg['string_array1'], ['def', 'ghi'])
        self.assertEqual(cfg['object1']['string2'], 'jkl')
        self.assertEqual(cfg['object1']['integer2'], 456)

    def test_empty(self):
        with self.assertRaises(error.Error):
            _test_config_from_content('')

    def test_invalid_content(self):
        with self.assertRaises(error.Error):
            _test_config_from_content('gaRbAge')

    def test_no_values(self):
        cfg = _test_config_from_content('{}')
        self.assertEqual(cfg['string1'], 'abc')
        self.assertEqual(cfg['integer1'], 123)
        self.assertEqual(cfg['string_array1'], ['def', 'ghi'])
        self.assertEqual(cfg['object1']['string2'], 'jkl')
        self.assertEqual(cfg['object1']['integer2'], 456)

    def test_file_overrides_default(self):
        cfg = _test_config_from_content('{ "string1": "ZYX", "object1": { "integer2": 987 } }')
        self.assertEqual(cfg['string1'], 'ZYX')
        self.assertEqual(cfg['integer1'], 123)
        self.assertEqual(cfg['string_array1'], ['def', 'ghi'])
        self.assertEqual(cfg['object1']['string2'], 'jkl')
        self.assertEqual(cfg['object1']['integer2'], 987)

    def test_unknown_property(self):
        with self.assertRaisesRegex(error.Error, 'unknown1'):
            _test_config_from_content('{ "unknown1": "foo" }')

        with self.assertRaisesRegex(error.Error, 'unknown2'):
            _test_config_from_content('{ "object1": { "unknown2": "foo" } }')

    def test_wrong_type(self):
        with self.assertRaises(error.Error):
            _test_config_from_content('{ "string1": 123 }')

    def test_wrong_type_in_array(self):
        with self.assertRaises(error.Error):
            _test_config_from_content('{ "string_array1": ["abc", 123] }')
