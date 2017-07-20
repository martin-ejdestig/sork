# This file is part of Sork.
#
# Copyright (C) 2016-2017 Martin Ejdestig <marejde@gmail.com>
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

import difflib
import subprocess

from . import check

from .. import string


def _custom_diff(path, content, formatted):
    content_lines = content.splitlines(True)
    formatted_lines = formatted.splitlines(True)
    diff_lines = []
    context = 1

    for group in difflib.SequenceMatcher(None,
                                         content_lines,
                                         formatted_lines).get_grouped_opcodes(context):
        first_line = group[0][1] + 1
        diff_lines.append('{}:{}: error: wrong format:\n'.format(path, first_line))

        for tag, content_start, content_end, formatted_start, formatted_end in group:
            if tag == 'equal':
                for line in content_lines[content_start:content_end]:
                    diff_lines.append(' ' + line)
            if tag in {'replace', 'delete'}:
                for line in content_lines[content_start:content_end]:
                    diff_lines.append('-' + line)
            if tag in {'replace', 'insert'}:
                for line in formatted_lines[formatted_start:formatted_end]:
                    diff_lines.append('+' + line)

    return diff_lines


class ClangFormatCheck(check.Check):
    NAME = 'clang-format'

    def check(self, source_file):
        with subprocess.Popen('clang-format',
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              cwd=self._environment.project_path,
                              universal_newlines=True) as process:
            stdout, stderr = process.communicate(input=source_file.content)
            if process.returncode != 0:
                return stderr

        diff_lines = _custom_diff(source_file.path, source_file.content, stdout)

        return string.rstrip_single_char(''.join(diff_lines), '\n')
