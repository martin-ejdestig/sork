# This file is part of Sork.
#
# Copyright (C) 2017-2018 Martin Ejdestig <marejde@gmail.com>
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

import json
import unittest.mock

from typing import Any

# Note: Prefer using actual commands even when testing. Only use this module
#       when doing so is very inconvenient.


class PopenMock(unittest.mock.MagicMock):
    def __init__(self,
                 *args,
                 stdout: Any = '',
                 stderr: str = '',
                 returncode: int = 0,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if not isinstance(stdout, str):
            stdout = json.dumps(stdout)

        context_mock = unittest.mock.MagicMock()
        context_mock.return_value.communicate.return_value = (stdout, stderr)
        context_mock.return_value.returncode = returncode

        self.return_value.__enter__ = context_mock

    # Defaults to returning type of self. Must override to avoid endless recursion due to
    # self.return_value, that creates a child mock, in __init__().
    def _get_child_mock(self, **kwargs) -> unittest.mock.MagicMock:
        return unittest.mock.MagicMock(**kwargs)


def patch(stdout: Any = '', stderr: str = '', returncode: int = 0):
    return unittest.mock.patch('subprocess.Popen',
                               new_callable=PopenMock,
                               stdout=stdout,
                               stderr=stderr,
                               returncode=returncode)
