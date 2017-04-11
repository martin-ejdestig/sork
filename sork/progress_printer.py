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

import sys
import threading


_CLEAR_ENTIRE_LINE = '\x1b[2K'


class ProgressPrinter:
    def __init__(self, output=None):
        self._output = sys.stdout if output is None else output
        self._lock = threading.Lock()
        self._info_string = ''
        self._item = ''
        self._count = 0
        self._done_count = 0
        self._aborted = False

    def start(self, info_string, done_count):
        with self._lock:
            self._info_string = info_string
            self._item = ''
            self._count = 0
            self._done_count = done_count
            self._aborted = False
            self._print_status()

    def abort(self):
        with self._lock:
            self._aborted = True
            self._print_status()

    def start_with_item(self, item):
        with self._lock:
            self._item = item
            self._print_status()

    def result(self, result):
        with self._lock:
            self._count += 1
            if result:
                self._print(str(result) + '\n')
            self._print_status()

    def _print_status(self):
        if self._count == self._done_count:
            trailing_str = '. Done.\n'
        elif self._aborted:
            trailing_str = '. Aborted.\n'
        elif self._item:
            trailing_str = ': ' + self._item
        else:
            trailing_str = '...'

        self._print('[{}/{}] {}{}'.format(self._count,
                                          self._done_count,
                                          self._info_string,
                                          trailing_str),
                    flush=True)

    def _print(self, string, flush=False):
        self._output.write(_CLEAR_ENTIRE_LINE + '\r' + string)

        if flush:
            self._output.flush()
