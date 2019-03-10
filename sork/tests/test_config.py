# This file is part of Sork.
#
# Copyright (C) 2017-2019 Martin Ejdestig <marejde@gmail.com>
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
#
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
import unittest

from .. import config


_TEST_CONFIG_SCHEMA = config.Schema({
    'string1': config.Value('abc'),
    'integer1': config.Value(123),
    'bool1': config.Value(False),
    'string_list1': config.Value(['def', 'ghi']),
    'integer_list1': config.Value([456], types=[config.ListType(int, min_length=1)]),
    'object1': config.Value({
        'string2': config.Value('jkl'),
        'integer2': config.Value(789)
    }),
    'multiple_types': config.Value('mno',
                                   types=[config.Type(str),
                                          config.Type(int),
                                          config.ListType(str)])
})


def _test_config_from_content(content: str) -> config.Config:
    with tempfile.NamedTemporaryFile(mode='wt') as file:
        file.write(content)
        file.flush()
        return config.create(file.name, _TEST_CONFIG_SCHEMA)


class ConfigTestCase(unittest.TestCase):
    def test_does_not_exist(self) -> None:
        cfg = config.create('does_not_exist', _TEST_CONFIG_SCHEMA)
        self.assertEqual(cfg['string1'], 'abc')
        self.assertEqual(cfg['integer1'], 123)
        self.assertEqual(cfg['bool1'], False)
        self.assertEqual(cfg['string_list1'], ['def', 'ghi'])
        self.assertEqual(cfg['integer_list1'], [456])
        self.assertEqual(cfg['object1']['string2'], 'jkl')
        self.assertEqual(cfg['object1']['integer2'], 789)
        self.assertEqual(cfg['multiple_types'], 'mno')

    def test_empty(self) -> None:
        with self.assertRaises(config.Error):
            _test_config_from_content('')

    def test_invalid_content(self) -> None:
        with self.assertRaises(config.Error):
            _test_config_from_content('gaRbAge')

    def test_no_values(self) -> None:
        cfg = _test_config_from_content('{}')
        self.assertEqual(cfg['string1'], 'abc')
        self.assertEqual(cfg['integer1'], 123)
        self.assertEqual(cfg['bool1'], False)
        self.assertEqual(cfg['string_list1'], ['def', 'ghi'])
        self.assertEqual(cfg['integer_list1'], [456])
        self.assertEqual(cfg['object1']['string2'], 'jkl')
        self.assertEqual(cfg['object1']['integer2'], 789)
        self.assertEqual(cfg['multiple_types'], 'mno')

    def test_file_overrides_default(self) -> None:
        cfg = _test_config_from_content('{ "string1": "ZYX", '
                                        '  "bool1": true, '
                                        '  "object1": { "integer2": 987 } }')
        self.assertEqual(cfg['string1'], 'ZYX')
        self.assertEqual(cfg['integer1'], 123)
        self.assertEqual(cfg['bool1'], True)
        self.assertEqual(cfg['string_list1'], ['def', 'ghi'])
        self.assertEqual(cfg['integer_list1'], [456])
        self.assertEqual(cfg['object1']['string2'], 'jkl')
        self.assertEqual(cfg['object1']['integer2'], 987)
        self.assertEqual(cfg['multiple_types'], 'mno')

    def test_unknown_property(self) -> None:
        with self.assertRaisesRegex(config.Error, 'unknown1'):
            _test_config_from_content('{ "unknown1": "foo" }')

        with self.assertRaisesRegex(config.Error, 'object1.unknown2'):
            _test_config_from_content('{ "object1": { "unknown2": "foo" } }')

    def test_wrong_type(self) -> None:
        with self.assertRaisesRegex(config.Error, 'string1'):
            _test_config_from_content('{ "string1": 123 }')

        with self.assertRaisesRegex(config.Error, 'string_list1'):
            _test_config_from_content('{ "string_list1": 123 }')

        with self.assertRaisesRegex(config.Error, 'object1.integer2'):
            _test_config_from_content('{ "object1": { "integer2": "foo" } }')

    def test_wrong_type_in_list(self) -> None:
        with self.assertRaisesRegex(config.Error, 'string_list1'):
            _test_config_from_content('{ "string_list1": [123] }')

        with self.assertRaisesRegex(config.Error, 'string_list1'):
            _test_config_from_content('{ "string_list1": ["abc", 123] }')

    def test_empty_list_ok(self) -> None:
        cfg = _test_config_from_content('{ "string_list1": [] }')
        self.assertEqual(cfg['string_list1'], [])

    def test_min_list_length(self) -> None:
        cfg = _test_config_from_content('{ "integer_list1": [9, 8] }')
        self.assertEqual(cfg['integer_list1'], [9, 8])

        with self.assertRaisesRegex(config.Error, 'integer_list1'):
            _test_config_from_content('{ "integer_list1": [] }')

    def test_bool_not_ok_as_int(self) -> None:
        # Explicitly test this since isinstance(True, int) == True.
        with self.assertRaisesRegex(config.Error, 'integer1'):
            _test_config_from_content('{ "integer1": true }')

        with self.assertRaisesRegex(config.Error, 'integer_list1'):
            _test_config_from_content('{ "integer_list1": [true] }')

    def test_multiple_types(self) -> None:
        cfg = _test_config_from_content('{ "multiple_types": "a string" }')
        self.assertEqual(cfg['multiple_types'], 'a string')

        cfg = _test_config_from_content('{ "multiple_types": 123456 }')
        self.assertEqual(cfg['multiple_types'], 123456)

        cfg = _test_config_from_content('{ "multiple_types": ["a", "list", "of", "strings"] }')
        self.assertEqual(cfg['multiple_types'], ['a', 'list', 'of', 'strings'])

        with self.assertRaisesRegex(config.Error, 'multiple_types'):
            _test_config_from_content('{ "multiple_types": true }')

        with self.assertRaisesRegex(config.Error, 'multiple_types'):
            _test_config_from_content('{ "multiple_types": [123, 456] }')


class ConfigSchemaValueConstructorTestCase(unittest.TestCase):
    def test_dict_must_be_str_value(self) -> None:
        self.assertRaises(ValueError, config.Value, {1: '2'})
        self.assertRaises(ValueError, config.Value, {1: config.Value('2')})
        self.assertRaises(ValueError, config.Value, {'1': 2})
        _ = config.Value({'1': config.Value(2)})

        self.assertRaises(ValueError, config.Value, {'1': config.Value(2), 3: config.Value(4)})
        self.assertRaises(ValueError, config.Value, {'1': config.Value(2), '3': 4})
        _ = config.Value({'1': config.Value(2), '3': config.Value(4)})

    def test_empty_list_must_have_type(self) -> None:
        self.assertRaises(ValueError, config.Value, [])
        _ = config.Value([], types=[config.ListType(int)])
        _ = config.Value([1])

    def test_default_type_check(self) -> None:
        self.assertRaises(ValueError, config.Value, 1, types=[config.Type(str)])
        self.assertRaises(ValueError, config.Value, 1, types=[config.Type(str), config.Type(bool)])
        _ = config.Value(1, types=[config.Type(str), config.Type(bool), config.Type(int)])
