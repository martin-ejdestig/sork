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

import os

from typing import List, Tuple

from ...project import Project
from ...source import SourceFile
from ...tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import clang_format
from ..check import Check


class ClangFormatTestCase(TestCaseWithTmpDir):
    def _create(self) -> Tuple[Project, Check]:
        self.create_tmp_build_dir('build')
        project = Project(self.tmp_path('.'), self.tmp_path('build'))
        return project, clang_format.create(project)

    def _create_source(self, project: Project, path: str, src_lines: List[str]) -> SourceFile:
        self.create_tmp_file(os.path.join(project.path, path), src_lines)
        return SourceFile(path, project)

    def _create_dot_clang_format(self, lines: List[str]):
        self.create_tmp_file('.clang-format', lines)

    def test_no_output_when_correctly_formatted(self):
        project, check = self._create()
        src = self._create_source(project, 'src/correct.cpp', [
            'void foo() {}',
            '',
            'int bar(int i) {',
            '  int j = i + 1;',
            '  return j;',
            '}'
        ])

        self.assertIsNone(check.run(src))

    def test_remove_and_add_lines(self):
        project, check = self._create()
        src = self._create_source(project, 'src/wrong.cpp', [
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
        output = check.run(src)

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
        project, check = self._create()
        src = self._create_source(project, 'src/wrong.cpp', ['void foo () {  }'])

        self.assertIn('src/wrong.cpp', check.run(src))

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

        project, check = self._create()
        src = self._create_source(project, 'src/baz/foo.cpp', [
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
        self.assertIsNone(check.run(src))

        self._create_dot_clang_format(cfg_lines('Regroup'))  # Now test that main header is moved.
        output = check.run(src)
        self.assertIsNotNone(output)
        self.assertIn('+#include "baz/foo.h"\n+\n', output)
        self.assertIn('-#include "baz/foo.h"\n', output)

    def test_line_number_for_hunk(self):
        project, check = self._create()
        lines_around_error = 8
        hunk_line_number = lines_around_error + 1 - clang_format.DIFF_CONTEXT
        src = self._create_source(project, 'src/foo.cpp',
                                  ['// bar'] * lines_around_error +
                                  [' int baz = 0;'] +
                                  ['// qux'] * lines_around_error)

        output = check.run(src)
        self.assertIn('src/foo.cpp:' + str(hunk_line_number), output)
