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

import sys
import threading

from typing import Any, Optional, TextIO


_CLEAR_ENTIRE_LINE = '\x1b[2K'

ABORTED_STR = 'Aborted'
DONE_STR = 'Done'


class ProgressPrinter:
    def __init__(self, output: Optional[TextIO] = None, verbose: bool = False) -> None:
        self._output: TextIO = sys.stdout if output is None else output
        self._verbose = verbose

        self._lock = threading.Lock()

        self._info_string = ''
        self._item = ''
        self._count = 0
        self._done_count = 0
        self._aborted = False

    def start(self, info_string: str, done_count: int) -> None:
        with self._lock:
            self._info_string = info_string
            self._item = ''
            self._count = 0
            self._done_count = done_count
            self._aborted = False
            self._print_status()

    def abort(self) -> None:
        with self._lock:
            self._aborted = True
            self._print_status()

    def start_with_item(self, item: str) -> None:
        with self._lock:
            if self._verbose:
                self._print('{}: {}\n'.format(self._info_string, item))
            else:
                self._item = item
            self._print_status()

    def done_with_item(self, output: Any) -> None:
        with self._lock:
            self._count += 1
            if output:
                self._print(str(output) + '\n')
            self._print_status()

    def _print_status(self) -> None:
        if self._count == self._done_count:
            trailing_str = '. ' + DONE_STR + '.\n'
        elif self._aborted:
            trailing_str = '. ' + ABORTED_STR + '.\n'
        elif self._item:
            trailing_str = ': ' + self._item
        else:
            trailing_str = '...'

        self._print('[{}/{}] {}{}'.format(self._count,
                                          self._done_count,
                                          self._info_string,
                                          trailing_str),
                    flush=True)

    def _print(self, string: str, flush: bool = False) -> None:
        self._output.write(_CLEAR_ENTIRE_LINE + '\r' + string)

        if flush:
            self._output.flush()
