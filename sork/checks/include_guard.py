# This file is part of Sork.
#
# Copyright (C) 2016-2018 Martin Ejdestig <marejde@gmail.com>
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
import re

from typing import Optional

from . import check

from .. import string
from ..project import Project
from ..source import SourceFile


class IncludeGuardCheck(check.Check):
    NAME = 'include_guard'

    def __init__(self, project: Project) -> None:
        super().__init__(project)

        config = project.config['checks.' + self.NAME]
        self._prefix = config['prefix']
        self._suffix = config['suffix']
        self._strip_paths = config['strip_paths']

        self._regex = re.compile(r"^(?:\s*|/\*.*?\*/|//[^\n]*)*"
                                 r"#ifndef\s+(\S*)\s*\n\s*"
                                 r"#define\s(\S*).*\n.*"
                                 r"#endif(?:\s+//\s+(?P<endif_comment>\S*))?\s*$",
                                 flags=re.DOTALL)

    def run(self, source_file: SourceFile) -> Optional[str]:
        if not source_file.is_header:
            return None

        match = self._regex.match(source_file.content)

        if not match:
            return '{}: error: missing include guard'.format(source_file.path)

        guard = self._include_guard_for_source_file(source_file)

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

    def _include_guard_for_source_file(self, source_file: SourceFile) -> str:
        stripped_path = self._strip_path(source_file.stem)
        path_part = re.sub(r"[ /\\-]", '_', stripped_path).upper()

        if path_part.startswith(self._prefix):
            path_part = path_part[len(self._prefix):]

        return ''.join([self._prefix, path_part, self._suffix])

    def _strip_path(self, path: str) -> str:
        for strip_path in self._strip_paths:
            if os.path.commonpath([path, strip_path]):
                return os.path.relpath(path, start=strip_path)

        return path
