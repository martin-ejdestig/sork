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

from .check_test_case import CheckTestCase

from ..clang_format import ClangFormatCheck


class ClangFormatTestCase(CheckTestCase):
    CHECK_CLASS = ClangFormatCheck

    def test_no_output_when_correctly_formatted(self):
        src = self.create_source('src/correct.cpp',
                                 'void foo() {}\n'
                                 '\n'
                                 'int bar(int i) {\n'
                                 '  int j = i + 1;\n'
                                 '  return j;\n'
                                 '}\n')
        self.assertEqual('', self._check.check(src))

    def test_remove_and_add_lines(self):
        src = self.create_source('src/wrong.cpp',
                                 'void foo()\n'
                                 '{\n'
                                 '}\n'
                                 '\n'
                                 'int bar( int  i)\n'
                                 ' { \n'
                                 '  int j = i+1;\n'
                                 '  return j;\n'
                                 '}\n')
        output = self._check.check(src)

        self.assertIn('-void foo()\n', output)
        self.assertIn('-{\n', output)
        self.assertIn('-}\n', output)
        self.assertIn('+void foo() {}\n', output)
        self.assertIn('-int bar( int  i)\n', output)
        self.assertIn('- { \n', output)
        self.assertIn('-  int j = i+1;\n', output)
        self.assertIn('+int bar(int i) {\n', output)
        self.assertIn('+  int j = i + 1;\n', output)

    def test_source_path(self):
        src = self.create_source('src/wrong.cpp', 'void foo () {  }\n')
        self.assertIn('src/wrong.cpp', self._check.check(src))

    def test_line_numbers_for_hunks(self):
        # TODO: Verify that line numbers hunks are correct. Make clang_format._DIFF_CONTEXT
        #       public to match exactly. (Line must be first error line - DIFF_CONTEXT.)
        pass

    def test_dot_clang_format_detected(self):
        # TODO: Write something to .clang_format in project root and make sure it affects
        #       formatting. Basically verifies that cwd is set to project root when running
        #       clang-format command.
        pass
