# This file is part of Sork.
#
# Copyright (C) 2017 Martin Ejdestig <marejde@gmail.com>
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
import os

from typing import Dict, List

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import error
from .. import paths
from ..compilation_database import CompilationDatabase


class CompilationDatabaseTestCase(TestCaseWithTmpDir):
    def _create_build_dir(self, path: str, database_list: List[Dict[str, str]]):
        self.create_tmp_file(os.path.join(path, paths.COMPILE_COMMANDS_JSON_PATH),
                             json.dumps(database_list))

    def test_load(self):
        self.create_tmp_file('foo/bar.cpp')
        self._create_build_dir('foo/build', [
            {
                'directory': self.tmp_path('foo/build'),
                'command': 'c++ ../bar.cpp',
                'file': '../bar.cpp'
            }
        ])
        self.create_tmp_dir('baz')

        for pwd, project_dir, build_dir in [('.', 'foo', 'foo/build'),
                                            ('foo', '.', 'build'),
                                            ('baz', '../foo', '../foo/build')]:
            with self.cd_tmp_dir(pwd):
                database = CompilationDatabase(project_dir, build_dir)

                command = database.get_command('bar.cpp')
                self.assertEqual('c++ ../bar.cpp', command.invokation)
                self.assertEqual(self.tmp_path('foo/build'), command.work_dir)
                self.assertEqual('../bar.cpp', command.file)

                self.assertIsNone(database.get_command('does_not_exist.cpp'))

    def test_does_not_exist(self):
        self.create_tmp_file('foo/bar.cpp')
        self.create_tmp_dir('foo/build')

        with self.cd_tmp_dir():
            with self.assertRaises(error.Error):
                _ = CompilationDatabase('foo', 'foo/build')
