# This file is part of Sork.
#
# Copyright (C) 2016-2019 Martin Ejdestig <marejde@gmail.com>
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

from typing import Optional

from .check import Check

from .. import string
from ..project import Project
from ..source import SourceFile


NAME = 'clang-format'

DIFF_CONTEXT = 1


def _custom_diff(path: str, content: str, formatted: str) -> str:
    content_lines = content.splitlines(True)
    formatted_lines = formatted.splitlines(True)
    diff_lines = []

    for group in difflib.SequenceMatcher(None,
                                         content_lines,
                                         formatted_lines).get_grouped_opcodes(DIFF_CONTEXT):
        first_line = int(group[0][1]) + 1  # difflib confuses mypy, unconfuse with int().
        diff_lines.append('{}:{}: error: wrong format:\n'.format(path, first_line))

        for opcode in group:
            tag, content_start, content_end, formatted_start, formatted_end = opcode
            if tag == 'equal':
                for line in content_lines[content_start:content_end]:
                    diff_lines.append(' ' + line)
            if tag in {'replace', 'delete'}:
                for line in content_lines[content_start:content_end]:
                    diff_lines.append('-' + line)
            if tag in {'replace', 'insert'}:
                for line in formatted_lines[formatted_start:formatted_end]:
                    diff_lines.append('+' + line)

    return ''.join(diff_lines)


def create(_: Project) -> Check:
    def run(source_file: SourceFile) -> Optional[str]:
        with subprocess.Popen(['clang-format', '-assume-filename=' + source_file.path],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              cwd=source_file.project.path,
                              universal_newlines=True) as process:
            stdout, stderr = process.communicate(input=source_file.content)
            if process.returncode != 0:
                return stderr

        diff_str = _custom_diff(source_file.path, source_file.content, stdout)

        return string.rstrip_single_char(diff_str, '\n') or None

    return Check(NAME, run)
