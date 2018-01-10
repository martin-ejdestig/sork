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

import re

from typing import List, Type, Set

from .check import Check
from .clang_format import ClangFormatCheck
from .clang_tidy import ClangTidyCheck
from .include_guard import IncludeGuardCheck
from .license_header import LicenseHeaderCheck

from .. import error
from ..project import Project


_CLASSES: List[Type[Check]] = [
    ClangFormatCheck,
    ClangTidyCheck,
    IncludeGuardCheck,
    LicenseHeaderCheck
]

NAMES = [c.NAME for c in _CLASSES]


class Error(error.Error):
    pass


def _strings_to_names(check_strings: List[str]) -> Set[str]:
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


def from_strings(project: Project, check_strings: List[str]) -> List[Check]:
    names = _strings_to_names(check_strings)

    if not names:
        raise Error('{} results in no checks.'.format(check_strings))

    return [c(project) for c in _CLASSES if c.NAME in names]
