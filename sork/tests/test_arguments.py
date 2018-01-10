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

import io
import os
import unittest
import unittest.mock

from typing import List

from .. import arguments


# Name of any valid command that takes source path(s).
_VALID_COMMAND = 'check'


class ArgumentsTestCase(unittest.TestCase):
    def test_jobs_must_be_greater_than_zero(self):
        def args(jobs: int) -> List[str]:
            return ['--jobs', str(jobs), _VALID_COMMAND]

        self.assertEqual(1, arguments.parse(args(1)).jobs)
        self.assertEqual(2, arguments.parse(args(2)).jobs)

        with unittest.mock.patch('sys.stderr', new=io.StringIO()):
            with self.assertRaises(SystemExit):
                _ = arguments.parse(args(0))

            with self.assertRaises(SystemExit):
                _ = arguments.parse(args(-1))

    def test_path_in_project_defaults_to_curdir(self):
        args = arguments.parse([_VALID_COMMAND])
        self.assertEqual(os.path.curdir, arguments.path_in_project(args))

    def test_path_in_project_from_command_source_path(self):
        args1 = arguments.parse([_VALID_COMMAND, 'test_dir'])
        self.assertEqual('test_dir', arguments.path_in_project(args1))

        args2 = arguments.parse([_VALID_COMMAND, 'test_file.cpp'])
        self.assertEqual('test_file.cpp', arguments.path_in_project(args2))
