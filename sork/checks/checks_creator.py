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

import re

from . import clang_format
from . import clang_tidy
from . import include_guard
from . import license_header

from .. import error


_CLASSES = [
    clang_format.ClangFormatCheck,
    clang_tidy.ClangTidyCheck,
    include_guard.IncludeGuardCheck,
    license_header.LicenseHeaderCheck
]

NAMES = [c.NAME for c in _CLASSES]


class ChecksCreator:
    def __init__(self, environment):
        self._environment = environment

    def create(self, check_strings, allow_none=True):
        names = self._strings_to_names(check_strings)

        if not names and not allow_none:
            raise error.Error('{} results in no checks.'.format(check_strings))

        return [c(self._environment) for c in _CLASSES if c.NAME in names]

    @staticmethod
    def _strings_to_names(check_strings):
        names_set = set()

        if not check_strings or check_strings[0].startswith('-'):
            names_set.update(NAMES)

        for check_string in check_strings:
            disable = check_string.startswith('-')
            names = [n for n in NAMES if re.match(check_string.lstrip('-'), n)]
            if disable:
                names_set.difference_update(names)
            else:
                names_set.update(names)

        return names_set
