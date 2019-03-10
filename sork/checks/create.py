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

import re

from typing import Callable, List, Tuple, Set

from .check import Check
from . import clang_format
from . import clang_tidy
from . import include_guard
from . import license_header

from .. import error
from ..project import Project


_CREATE_FUNCTIONS: List[Tuple[str, Callable[[Project], Check]]] = [
    (clang_format.NAME, clang_format.create),
    (clang_tidy.NAME, clang_tidy.create),
    (include_guard.NAME, include_guard.create),
    (license_header.NAME, license_header.create)
]

NAMES = [name for (name, _) in _CREATE_FUNCTIONS]


class Error(error.Error):
    pass


def from_strings(project: Project, check_strings: List[str]) -> List[Check]:
    def strings_to_names(check_strings: List[str]) -> Set[str]:
        names_set = set()

        if not check_strings or check_strings[0].startswith('-'):
            names_set.update(NAMES)

        for check_string in check_strings:
            disable = check_string.startswith('-')
            match_str = check_string.lstrip('-')
            names = [n for n in NAMES if re.match(match_str, n)]

            if not names:
                raise Error('{} does not match any of the available checks ({}).'.
                            format(match_str, ', '.join(NAMES)))

            if disable:
                names_set.difference_update(names)
            else:
                names_set.update(names)

        return names_set

    names = strings_to_names(check_strings)

    if not names:
        raise Error('{} results in no checks.'.format(check_strings))

    return [create(project) for (name, create) in _CREATE_FUNCTIONS if name in names]
