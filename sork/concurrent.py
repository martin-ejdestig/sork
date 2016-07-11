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

import concurrent.futures

from . import progress_printer


def for_each_with_progress_printer(info_string, func, values, num_threads=None):
    aborted = False
    printer = progress_printer.ProgressPrinter()

    def wrapped_func(value):
        return None if aborted else func(value)

    printer.start(info_string, len(values))

    with concurrent.futures.ThreadPoolExecutor(num_threads) as executor:
        try:
            futures = [executor.submit(wrapped_func, value) for value in values]
            for future in concurrent.futures.as_completed(futures):
                printer.result(future.result())
        except:
            aborted = True
            printer.abort()
            raise
