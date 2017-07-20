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

import concurrent.futures

from typing import Callable, Optional, Sequence, TypeVar


T = TypeVar('T')


def for_each(func: Callable[[T], None], values: Sequence[T], num_threads: Optional[int] = None):
    aborted = False

    def wrapped_func(value):
        if not aborted:
            func(value)

    with concurrent.futures.ThreadPoolExecutor(num_threads) as executor:
        try:
            futures = [executor.submit(wrapped_func, value) for value in values]
            concurrent.futures.wait(futures)
        except BaseException:
            aborted = True
            raise
