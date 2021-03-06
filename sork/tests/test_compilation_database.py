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

import os

from typing import Any, Dict, List, Tuple

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from ..compilation_database import CompilationDatabase, Error


class CompilationDatabaseTestCase(TestCaseWithTmpDir):
    def test_load_success(self) -> None:
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_file('foo/src/baz.cpp')
        self.create_tmp_file('foo/src/absolute.cpp')
        self.create_tmp_dir('qux')
        self.create_tmp_comp_db('foo/build', [
            {
                'directory': self.tmp_path('foo/build'),
                'command': 'c++ -o src/bar.o -c ../src/bar.cpp',
                'file': '../src/bar.cpp'
            },
            {
                'directory': self.tmp_path('foo/build'),
                'command': 'c++ -o src/baz.o -c ../src/baz.cpp',
                'file': '../src/baz.cpp'
            },
            {
                'directory': self.tmp_path('foo/build'),
                'command': '/usr/bin/c++ -o src/absolute.o -c ' +
                           self.tmp_path('foo/src/absolute.cpp'),
                'file': self.tmp_path('foo/src/absolute.cpp')
            }
        ])

        for cd_path, project_dir, build_dir in [('.', 'foo', 'foo/build'),
                                                ('foo', '.', 'build'),
                                                ('foo/src', '..', '../build'),
                                                ('qux', '../foo', '../foo/build')]:
            with self.cd_tmp_dir(cd_path):
                database = CompilationDatabase(project_dir, build_dir)

                command = database.commands.get('src/bar.cpp')
                self.assertIsNotNone(command)
                assert command  # mypy does not get that assertIsNotNone makes this redundant.
                self.assertEqual('c++ -o src/bar.o -c ../src/bar.cpp', command.invocation)
                self.assertEqual(self.tmp_path('foo/build'), command.work_dir)
                self.assertEqual('../src/bar.cpp', command.file)

                command = database.commands.get('src/baz.cpp')
                self.assertIsNotNone(command)
                assert command  # mypy does not get that assertIsNotNone makes this redundant.
                self.assertEqual('c++ -o src/baz.o -c ../src/baz.cpp', command.invocation)
                self.assertEqual(self.tmp_path('foo/build'), command.work_dir)
                self.assertEqual('../src/baz.cpp', command.file)

                command = database.commands.get('src/absolute.cpp')
                self.assertIsNotNone(command)
                assert command  # mypy does not get that assertIsNotNone makes this redundant.
                self.assertEqual('/usr/bin/c++ -o src/absolute.o -c ' +
                                 self.tmp_path('foo/src/absolute.cpp'), command.invocation)
                self.assertEqual(self.tmp_path('foo/build'), command.work_dir)
                self.assertTrue(os.path.isabs(command.file))
                self.assertEqual(self.tmp_path('foo/src/absolute.cpp'), command.file)

                self.assertIsNone(database.commands.get('does_not_exist.cpp'))

    def test_no_entries(self) -> None:
        self.create_tmp_comp_db('foo/build', [])

        with self.cd_tmp_dir():
            _ = CompilationDatabase('foo', 'foo/build')

    def test_does_not_exist(self) -> None:
        self.create_tmp_dir('foo/build')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(Error, self.comp_db_path('foo/build')):
                _ = CompilationDatabase('foo', 'foo/build')

    def test_top_level_dict(self) -> None:
        self.create_tmp_comp_db('foo/build', '{}')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(Error, self.comp_db_path('foo/build')):
                _ = CompilationDatabase('foo', 'foo/build')

    def test_garbage(self) -> None:
        self.create_tmp_comp_db('foo/build', 'garbage')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(Error, self.comp_db_path('foo/build')):
                _ = CompilationDatabase('foo', 'foo/build')

    def test_invalid_entries(self) -> None:
        dir_paths_and_db_lists: List[Tuple[str, List[Dict[str, Any]]]] = [
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
            self.create_tmp_comp_db(os.path.join(dir_path, 'build'), db_list)

        with self.cd_tmp_dir():
            for dir_path, _ in dir_paths_and_db_lists:
                build_path = os.path.join(dir_path, 'build')
                with self.assertRaisesRegex(Error, self.comp_db_path(build_path)):
                    _ = CompilationDatabase(dir_path, build_path)
