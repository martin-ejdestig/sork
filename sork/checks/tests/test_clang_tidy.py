# This file is part of Sork.
#
# Copyright (C) 2018 Martin Ejdestig <marejde@gmail.com>
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

from typing import List

from .check_test_case import CheckTestCase

from ..clang_tidy import ClangTidyCheck


class ClangTidyTestCase(CheckTestCase):
    CHECK_CLASS = ClangTidyCheck

    def _create_dot_clang_tidy(self, lines: List[str]):
        self.create_tmp_file('.clang-tidy', '\n'.join(lines))

    def test_no_error_returns_none(self):
        check = self.create_check(comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self.create_source('src/foo.cpp', ['int *p = nullptr;'])
        self._create_dot_clang_tidy(['Checks: "modernize-use-nullptr"'])

        self.assertIsNone(check.check(src))

    def test_error_position_in_output(self):
        check = self.create_check(comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self.create_source('src/foo.cpp', ['int *p = 0;'])
        self._create_dot_clang_tidy(['Checks: "modernize-use-nullptr"'])

        self.assertIn('src/foo.cpp:1:10', check.check(src))

    def test_source_without_compile_command_is_ignored(self):
        check = self.create_check(comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self.create_source('src/bar.cpp', ['int *p = 0;'])
        self._create_dot_clang_tidy(['Checks: "modernize-use-nullptr"'])

        self.assertIsNone(check.check(src))

    def test_gcc_specific_warning_flags_ignored(self):
        check = self.create_check(comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'g++ -Wsuggest-override -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self.create_source('src/bar.cpp', [''])

        self.assertIsNone(check.check(src))

    def test_absolute_compiler_path_replaced_correctly(self):
        check = self.create_check(comp_db=[{
            'directory': self.tmp_path('build'),
            'command': '/usr/bin/c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self.create_source('src/foo.cpp', ['int *p = 0;'])
        self._create_dot_clang_tidy(['Checks: "modernize-use-nullptr"'])

        self.assertIn('src/foo.cpp:1:10', check.check(src))
