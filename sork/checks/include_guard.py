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

import os
import re

from .. import check
from .. import string


def _strip_path(path, strip_paths):
    for strip_path in strip_paths:
        if os.path.commonpath([path, strip_path]):
            return os.path.relpath(path, start=strip_path)
    return path


def _include_guard_for_source_file(source_file):
    config = source_file.environment.config['checks.include_guard']

    stripped_path = _strip_path(source_file.stem, config['strip_paths'])

    return ''.join([config['prefix'],
                    re.sub(r"[ /\\-]", '_', stripped_path).upper(),
                    config['suffix']])


class IncludeGuardCheck(check.Check):
    def __init__(self):
        super().__init__()

    def check(self, source_file):
        if not source_file.is_header:
            return

        match = re.match(r"^(?:\s*|/\*.*?\*/|//[^\n]*)*"
                         r"#ifndef\s+(\S*)\s*\n\s*"
                         r"#define\s(\S*).*\n.*"
                         r"#endif\s+//\s+(\S*)\s*$",
                         source_file.content,
                         flags=re.DOTALL)
        if not match:
            return '{}: error: missing include guard'.format(source_file.path)

        guard = _include_guard_for_source_file(source_file)

        error_positions = [string.index_to_line_and_column(source_file.content, match.start(group))
                           for group, found_guard in enumerate(match.groups(), start=1)
                           if found_guard != guard]

        output = ['{}:{}:{}: error: include guard name should be {}'.format(source_file.path,
                                                                            *position,
                                                                            guard)
                  for position in error_positions]

        return '\n'.join(output)
