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

import sys


_CLEAR_ENTIRE_LINE = '\x1b[2K'


class ProgressPrinter:
    def __init__(self):
        self._info_string = ''
        self._count = 0
        self._done_count = 0
        self._aborted = False

    def start(self, info_string, done_count):
        self._info_string = info_string
        self._count = 0
        self._done_count = done_count
        self._aborted = False
        self._print()

    def abort(self):
        self._aborted = True
        self._print()

    def result(self, result):
        self._count += 1
        if result:
            sys.stdout.write(_CLEAR_ENTIRE_LINE + '\r' + str(result) + '\n')
        self._print()

    def _print(self):
        if self._count == self._done_count:
            trailing_str = '. Done.\n'
        elif self._aborted:
            trailing_str = '. Aborted.\n'
        else:
            trailing_str = '...'

        sys.stdout.write('\r[{}/{}] {}{}'.format(self._count,
                                                 self._done_count,
                                                 self._info_string,
                                                 trailing_str))
        sys.stdout.flush()
