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

from ..clang_format import ClangFormatCheck, DIFF_CONTEXT


class ClangFormatTestCase(CheckTestCase):
    CHECK_CLASS = ClangFormatCheck

    def _create_dot_clang_format(self, lines: List[str]):
        self.create_tmp_file('.clang-format', lines)

    def test_no_output_when_correctly_formatted(self):
        check = self.create_check()
        src = self.create_source('src/correct.cpp', [
            'void foo() {}',
            '',
            'int bar(int i) {',
            '  int j = i + 1;',
            '  return j;',
            '}'
        ])

        self.assertIsNone(check.check(src))

    def test_remove_and_add_lines(self):
        check = self.create_check()
        src = self.create_source('src/wrong.cpp', [
            'void foo()',
            '{',
            '}',
            '',
            'int bar( int  i)',
            ' { ',
            '  int j = i+1;',
            '  return j;',
            '}'
        ])
        output = check.check(src)

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
        check = self.create_check()
        src = self.create_source('src/wrong.cpp', ['void foo () {  }'])

        self.assertIn('src/wrong.cpp', check.check(src))

    def test_assume_filename(self):
        # File content is passed to clang-format through stdin which means -assume-filename argument
        # must be used for clang-format to know name of file. Sorting of include blocks, where main
        # header gets prio 0 (see clang-format documentation), requires this so use it to test.
        def cfg_lines(include_blocks_value: str):
            return ['IncludeBlocks: ' + include_blocks_value,
                    'IncludeCategories:',
                    '  - Regex: \'^<.*\\.h>\'',
                    '    Priority: 1',
                    '  - Regex: \'^<.*\'',
                    '    Priority: 2',
                    '  - Regex: \'.*\'',
                    '    Priority: 3']

        check = self.create_check()
        src = self.create_source('src/baz/foo.cpp', [
            '#include <stdio.h>',
            '#include <stdlib.h>',
            '',
            '#include <algorithm>',
            '#include <vector>',
            '',
            '#include "bar.h"',
            '#include "baz/foo.h"',
            '#include "baz/qux.h"'
        ])

        self._create_dot_clang_format(cfg_lines('Preserve'))  # Verify that formatted correctly.
        self.assertIsNone(check.check(src))

        self._create_dot_clang_format(cfg_lines('Regroup'))  # Now test that main header is moved.
        output = check.check(src)
        self.assertIsNotNone(output)
        self.assertIn('+#include "baz/foo.h"\n+\n', output)
        self.assertIn('-#include "baz/foo.h"\n', output)

    def test_line_number_for_hunk(self):
        check = self.create_check()
        lines_around_error = 8
        hunk_line_number = lines_around_error + 1 - DIFF_CONTEXT
        src = self.create_source('src/foo.cpp',
                                 ['// bar'] * lines_around_error +
                                 [' int baz = 0;'] +
                                 ['// qux'] * lines_around_error)

        output = check.check(src)
        self.assertIn('src/foo.cpp:' + str(hunk_line_number), output)
