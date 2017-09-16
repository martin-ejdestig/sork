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

from typing import Any, Dict, List, Union

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import paths
from ..compilation_database import CompilationDatabase, Error


def _db_path(build_path: str):
    return os.path.join(build_path, paths.COMPILE_COMMANDS_JSON_PATH)


class CompilationDatabaseTestCase(TestCaseWithTmpDir):
    def _create_db(self, path: str, content: Union[List[Dict[str, Any]], str]):
        if not isinstance(content, str):
            content = json.dumps(content)
        self.create_tmp_file(_db_path(path), content)

    def test_load_success(self):
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_file('foo/src/baz.cpp')
        self.create_tmp_dir('qux')
        self._create_db('foo/build', [
            {
                'directory': self.tmp_path('foo/build'),
                'command': 'c++ -o src/bar.o -c ../src/bar.cpp',
                'file': '../src/bar.cpp'
            },
            {
                'directory': self.tmp_path('foo/build'),
                'command': 'c++ -o src/baz.o -c ../src/baz.cpp',
                'file': '../src/baz.cpp'
            }
        ])

        for cd_path, project_dir, build_dir in [('.', 'foo', 'foo/build'),
                                                ('foo', '.', 'build'),
                                                ('foo/src', '..', '../build'),
                                                ('qux', '../foo', '../foo/build')]:
            with self.cd_tmp_dir(cd_path):
                database = CompilationDatabase(project_dir, build_dir)

                command = database.get_command('src/bar.cpp')
                self.assertEqual('c++ -o src/bar.o -c ../src/bar.cpp', command.invokation)
                self.assertEqual(self.tmp_path('foo/build'), command.work_dir)
                self.assertEqual('../src/bar.cpp', command.file)

                command = database.get_command('src/baz.cpp')
                self.assertEqual('c++ -o src/baz.o -c ../src/baz.cpp', command.invokation)
                self.assertEqual(self.tmp_path('foo/build'), command.work_dir)
                self.assertEqual('../src/baz.cpp', command.file)

                self.assertIsNone(database.get_command('does_not_exist.cpp'))

    def test_no_entries(self):
        self._create_db('foo/build', [])

        with self.cd_tmp_dir():
            _ = CompilationDatabase('foo', 'foo/build')

    def test_does_not_exist(self):
        self.create_tmp_dir('foo/build')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(Error, _db_path('foo/build')):
                _ = CompilationDatabase('foo', 'foo/build')

    def test_top_level_dict(self):
        self._create_db('foo/build', '{}')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(Error, _db_path('foo/build')):
                _ = CompilationDatabase('foo', 'foo/build')

    def test_garbage(self):
        self._create_db('foo/build', 'garbage')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(Error, _db_path('foo/build')):
                _ = CompilationDatabase('foo', 'foo/build')

    def test_invalid_entries(self):
        dir_paths_and_db_lists = [
            ('directory_missing', [{'command': 'c++ -o src/bar.o -c ../src/bar.cpp',
                                    'file': '../src/bar.cpp'}]),
            ('command_missing', [{'directory': self.tmp_path('command_missing/build'),
                                  'file': '../src/bar.cpp'}]),
            ('file_missing', [{'directory': self.tmp_path('file_missing/build'),
                               'command': 'c++ -o src/bar.o -c ../src/bar.cpp'}]),
            ('directory_wrong_type', [{'directory': 123,
                                       'command': 'c++ -o src/bar.o -c ../src/bar.cpp',
                                       'file': '../src/bar.cpp'}]),
            ('command_wrong_type', [{'directory': self.tmp_path('command_wrong_type/build'),
                                     'command': 123,
                                     'file': '../src/bar.cpp'}]),
            ('file_wrong_type', [{'directory': self.tmp_path('file_wrong_type/build'),
                                  'command': 'c++ -o src/bar.o -c ../src/bar.cpp',
                                  'file': 123}])
        ]

        for dir_path, db_list in dir_paths_and_db_lists:
            self.create_tmp_file(os.path.join(dir_path, 'src/bar.cpp'))
            self._create_db(os.path.join(dir_path, 'build'), db_list)

        with self.cd_tmp_dir():
            for dir_path, _ in dir_paths_and_db_lists:
                build_path = os.path.join(dir_path, 'build')
                with self.assertRaisesRegex(Error, _db_path(build_path), msg=dir_path):
                    _ = CompilationDatabase(dir_path, build_path)
