# This file is part of Sork.
#
# Copyright (C) 2017-2019 Martin Ejdestig <marejde@gmail.com>
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

import io
import random
import string
import unittest

from typing import List

from .. import progress_printer


class TestProgressPrinter(progress_printer.ProgressPrinter):
    def __init__(self, verbose: bool = False) -> None:
        self._io = io.StringIO()
        super().__init__(output=self._io, verbose=verbose)

    @property
    def value(self) -> str:
        return self._io.getvalue()


def _random_string() -> str:
    return ''.join(random.choices(string.ascii_letters, k=10))


def _random_strings(count: int) -> List[str]:
    return [_random_string() for _ in range(count)]


class ProgressPrinterTestCase(unittest.TestCase):
    def test_start_prints_info_and_count(self) -> None:
        printer = TestProgressPrinter()
        printer.start('Foo', 123)
        self.assertIn('Foo', printer.value)
        self.assertIn('123', printer.value)

    def test_abort_prints_aborted_and_newline(self) -> None:
        printer = TestProgressPrinter()
        printer.start('Foo', 123)
        self.assertNotIn(progress_printer.ABORTED_STR, printer.value)
        printer.abort()
        self.assertRegex(printer.value, progress_printer.ABORTED_STR + r".*\n")

    def test_done_not_printed_until_done(self) -> None:
        printer = TestProgressPrinter()
        items = _random_strings(4)
        printer.start('Foo', len(items))

        for item in items:
            printer.start_with_item(item)
            self.assertNotIn(progress_printer.DONE_STR, printer.value)
            printer.done_with_item(None)

        self.assertRegex(printer.value, progress_printer.DONE_STR + r".*\n")

    def test_progress(self) -> None:
        for verbose in [False, True]:
            printer = TestProgressPrinter(verbose=verbose)
            items = _random_strings(10)
            printer.start('Foo', len(items))

            for i, item in enumerate(items):
                printer.start_with_item(item)
                self.assertIn(str(i), printer.value)
                self.assertRegex(printer.value, item + ('\n' if verbose else ''))

                output = _random_string() if i % 3 == 0 else None

                printer.done_with_item(output)
                self.assertIn(str(i + 1), printer.value)
                if output:
                    self.assertRegex(printer.value, output + '\n')
