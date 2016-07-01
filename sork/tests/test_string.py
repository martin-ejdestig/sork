# This file is part of Sork.
#
# Copyright (C) 2016 Martin Ejdestig <marejde@gmail.com>
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

import unittest

from .. import string


class TestString(unittest.TestCase):
    def test_index_to_line_and_column(self):
        self.assertEqual(string.index_to_line_and_column('a', 0), (1, 1))

        self.assertEqual(string.index_to_line_and_column('ab', 0), (1, 1))
        self.assertEqual(string.index_to_line_and_column('ab', 1), (1, 2))

        self.assertEqual(string.index_to_line_and_column('\n', 0), (1, 1))

        self.assertEqual(string.index_to_line_and_column('a\n', 0), (1, 1))
        self.assertEqual(string.index_to_line_and_column('a\n', 1), (1, 2))

        self.assertEqual(string.index_to_line_and_column('a\nb', 0), (1, 1))
        self.assertEqual(string.index_to_line_and_column('a\nb', 1), (1, 2))
        self.assertEqual(string.index_to_line_and_column('a\nb', 2), (2, 1))

        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 0), (1, 1))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 1), (1, 2))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 2), (1, 3))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 3), (1, 4))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 4), (2, 1))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 5), (2, 2))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 6), (3, 1))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 7), (3, 2))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 8), (3, 3))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 9), (4, 1))
        self.assertEqual(string.index_to_line_and_column('abc\nd\nef\ngh', 10), (4, 2))

        self.assertRaises(ValueError, string.index_to_line_and_column, '', 0)
        self.assertRaises(ValueError, string.index_to_line_and_column, '', 1)
        self.assertRaises(ValueError, string.index_to_line_and_column, '', -1)
        self.assertRaises(ValueError, string.index_to_line_and_column, 'a', 1)
        self.assertRaises(ValueError, string.index_to_line_and_column, 'a', -1)
        self.assertRaises(ValueError, string.index_to_line_and_column, 'ab', 2)
        self.assertRaises(ValueError, string.index_to_line_and_column, 'ab', -1)
        self.assertRaises(ValueError, string.index_to_line_and_column, 'abc\nd\nef\ngh', 11)

    def test_rstrip_single_char(self):
        self.assertEqual(string.rstrip_single_char('abc'), 'abc')
        self.assertEqual(string.rstrip_single_char('abc '), 'abc')
        self.assertEqual(string.rstrip_single_char('abc  '), 'abc ')
        self.assertEqual(string.rstrip_single_char(' abc'), ' abc')

        self.assertEqual(string.rstrip_single_char('abc', 'a'), 'abc')
        self.assertEqual(string.rstrip_single_char('abc', 'b'), 'abc')
        self.assertEqual(string.rstrip_single_char('abc', 'c'), 'ab')
        self.assertEqual(string.rstrip_single_char('abc', 'bc'), 'ab')
        self.assertEqual(string.rstrip_single_char('abc', 'cb'), 'ab')
        self.assertEqual(string.rstrip_single_char('abc', 'ab'), 'abc')

        self.assertEqual(string.rstrip_single_char(''), '')
