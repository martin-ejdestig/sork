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

from . import checks
from . import concurrent
from . import source


def _check_source_file(source_file):
    outputs = []

    if source_file.compile_command:
        outputs.append(checks.clang_tidy.check(source_file))

    if source_file.is_header:
        outputs.append(checks.include_guard.check(source_file))

    outputs.append(checks.clang_format.check(source_file))

    return '\n'.join(o for o in outputs if o)


def check(environment):
    concurrent.for_each_with_progress_printer('Checking source',
                                              _check_source_file,
                                              source.find_source_files(environment))
