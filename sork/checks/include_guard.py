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
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re

from typing import Optional

from .check import Check

from .. import string
from ..project import Project
from ..source import SourceFile


NAME = 'include_guard'


def create(project: Project) -> Check:
    def transform_path(path: str) -> str:
        return re.sub(r"[ /\\-]", '_', path).upper()

    def prefix_from_basepath(path: str) -> str:
        return transform_path(os.path.basename(os.path.abspath(path))) + '_'

    config = project.config['checks.' + NAME]
    prefix = config['prefix'] or prefix_from_basepath(project.path)
    suffix = config['suffix']
    strip_paths = config['strip_paths']

    regex = re.compile(r"^(?:\s*|/\*.*?\*/|//[^\n]*)*"
                       r"#ifndef\s+(\S*)\s*\n\s*"
                       r"#define\s(\S*).*\n.*"
                       r"#endif(?:\s+//\s+(?P<endif_comment>\S*))?\s*$",
                       flags=re.DOTALL)

    def strip_path(path: str) -> str:
        for strip_path in strip_paths:
            if os.path.commonpath([path, strip_path]):
                return os.path.relpath(path, start=strip_path)

        return path

    def include_guard_for_source_file(source_file: SourceFile) -> str:
        stripped_path = strip_path(source_file.stem)
        path_part = transform_path(stripped_path)

        if path_part.startswith(prefix):
            path_part = path_part[len(prefix):]

        return ''.join([prefix, path_part, suffix])

    def run(source_file: SourceFile) -> Optional[str]:
        if not source_file.is_header:
            return None

        match = regex.match(source_file.content)

        if not match:
            return '{}: error: missing include guard'.format(source_file.path)

        guard = include_guard_for_source_file(source_file)

        error_positions = [string.index_to_line_and_column(source_file.content, match.start(group))
                           for group, found_guard in enumerate(match.groups(), start=1)
                           if found_guard and found_guard != guard]

        output = ['{}:{}:{}: error: include guard name should be {}'.format(source_file.path,
                                                                            *position,
                                                                            guard)
                  for position in error_positions]

        if not match.group('endif_comment'):
            output.append('{}: error: missing include guard #endif comment'.
                          format(source_file.path))

        return '\n'.join(output)

    return Check(NAME, run)
