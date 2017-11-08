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

import itertools
import os

from typing import List, Optional

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from ..source import Error, SourceFile, SourceFinder
from ..project import Project


class SourceFileTestCase(TestCaseWithTmpDir):
    def test_compile_command(self):
        self.create_tmp_build_dir('build', comp_db=[
            {
                'directory': self.tmp_path('build'),
                'command': 'c++ -o foo.o -c ../foo.cpp',
                'file': '../foo.cpp'
            },
            {
                'directory': self.tmp_path('build'),
                'command': 'c++ -o bar.o -c ../bar.cpp',
                'file': '../bar.cpp'
            }
        ])

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            foo_src = SourceFile('foo.cpp', project)
            bar_src = SourceFile('bar.cpp', project)
            no_compile_command_src = SourceFile('has_no_compile_command.cpp', project)

            self.assertEqual(self.tmp_path('build'), foo_src.compile_command.work_dir)
            self.assertEqual('c++ -o foo.o -c ../foo.cpp', foo_src.compile_command.invocation)
            self.assertEqual('../foo.cpp', foo_src.compile_command.file)

            self.assertEqual(self.tmp_path('build'), bar_src.compile_command.work_dir)
            self.assertEqual('c++ -o bar.o -c ../bar.cpp', bar_src.compile_command.invocation)
            self.assertEqual('../bar.cpp', bar_src.compile_command.file)

            self.assertIsNone(no_compile_command_src.compile_command)

    def test_content(self):
        content = 'void foo()\n{\n}\n'
        self.create_tmp_file('src/foo.cpp', content)
        self.create_tmp_build_dir('build')

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            src_file = SourceFile('src/foo.cpp', project)
            does_not_exist = SourceFile('src/does_not_exist.cpp', project)

            self.assertEqual(content, src_file.content)
            with self.assertRaisesRegex(FileNotFoundError, 'src/does_not_exist.cpp'):
                _ = does_not_exist.content

    def test_content_absolute_project_path(self):
        content = 'void foo()\n{\n}\n'
        self.create_tmp_file('src/foo.cpp', content)
        self.create_tmp_build_dir('build')

        project = Project(self.tmp_path('.'), self.tmp_path('build'))
        src_file = SourceFile('src/foo.cpp', project)

        self.assertEqual(content, src_file.content)

    def test_is_header(self):
        self.create_tmp_build_dir('build')
        project = Project(self.tmp_path('.'), self.tmp_path('build'))

        self.assertTrue(SourceFile('abc.h', project).is_header)
        self.assertTrue(SourceFile('def.h.in', project).is_header)
        self.assertFalse(SourceFile('ghi.cpp', project).is_header)
        self.assertFalse(SourceFile('jkl.cpp.in', project).is_header)
        self.assertFalse(SourceFile('mno.c', project).is_header)
        self.assertFalse(SourceFile('pqr.c.in', project).is_header)
        self.assertFalse(SourceFile('stu', project).is_header)
        self.assertFalse(SourceFile('vxy.in', project).is_header)

    def test_stem(self):
        self.create_tmp_build_dir('build')
        project = Project(self.tmp_path('.'), self.tmp_path('build'))

        self.assertEqual('abc', SourceFile('abc.h', project).stem)
        self.assertEqual('def', SourceFile('def.h.in', project).stem)
        self.assertEqual('ghi', SourceFile('ghi.cpp', project).stem)
        self.assertEqual('jkl', SourceFile('jkl.cpp.in', project).stem)
        self.assertEqual('mno', SourceFile('mno.c', project).stem)
        self.assertEqual('pqr', SourceFile('pqr.c.in', project).stem)
        self.assertEqual('stu', SourceFile('stu', project).stem)
        self.assertEqual('vxy', SourceFile('vxy.in', project).stem)


class SourceFinderTestCase(TestCaseWithTmpDir):
    def _assert_paths(self,
                      paths: List[str],
                      src_files: List[SourceFile],
                      msg: Optional[str] = None):
        self.assertEqual(paths, [src_file.path for src_file in src_files], msg)

    def test_find_files(self):
        src_paths = [
            'src/abc.cpp',
            'src/abc.h',
            'src/config.h.in',
            'src/def/ghi.cpp',
            'src/def/ghi.h',
            'src/jkl/mno/pqr.cpp',
            'src/jkl/mno/pqr.h',
            'top_level.cpp',
            'top_level.h'
        ]
        for path in src_paths:
            self.create_tmp_file(os.path.join('foo', path))

        self.create_tmp_build_dir('build')

        # Different work dirs.
        for cwd, project_path, build_path in [('.', 'foo', 'build'),
                                              ('foo', '.', '../build'),
                                              ('foo/src', '..', '../../build'),
                                              ('foo/src/def', '../..', '../../../build'),
                                              ('build', '../foo', '.')]:
            with self.cd_tmp_dir(cwd):
                project = Project(project_path, build_path)
                src_files = SourceFinder(project).find_files()
                self._assert_paths(src_paths, src_files, msg='cwd={}'.format(cwd))

        with self.cd_tmp_dir('foo'):
            project = Project('.', '../build')
            finder = SourceFinder(project)

            # Empty paths same as none.
            self._assert_paths(src_paths, finder.find_files([]))

            # Single subdir.
            self._assert_paths(['src/def/ghi.cpp', 'src/def/ghi.h'],
                               finder.find_files(['src/def']))
            self._assert_paths(['src/jkl/mno/pqr.cpp', 'src/jkl/mno/pqr.h'],
                               finder.find_files(['src/jkl']))
            self._assert_paths(['src/jkl/mno/pqr.cpp', 'src/jkl/mno/pqr.h'],
                               finder.find_files(['src/jkl/mno']))

            # Single file.
            self._assert_paths(['src/abc.cpp'], finder.find_files(['src/abc.cpp']))
            self._assert_paths(['src/def/ghi.h'], finder.find_files(['src/def/ghi.h']))
            self._assert_paths(['src/jkl/mno/pqr.cpp'], finder.find_files(['src/jkl/mno/pqr.cpp']))
            self._assert_paths(['top_level.h'], finder.find_files(['top_level.h']))

            # Subdir and file. Always sorted the same.
            for find_paths in itertools.permutations(['src/abc.cpp', 'src/def']):
                self._assert_paths(['src/abc.cpp', 'src/def/ghi.cpp', 'src/def/ghi.h'],
                                   finder.find_files(find_paths))

            # Two subdirs and one file. Always sorted the same.
            for find_paths in itertools.permutations(['src/abc.cpp', 'src/def', 'src/jkl']):
                self._assert_paths(['src/abc.cpp', 'src/def/ghi.cpp', 'src/def/ghi.h',
                                    'src/jkl/mno/pqr.cpp', 'src/jkl/mno/pqr.h'],
                                   finder.find_files(find_paths))

    def test_find_file(self):
        self.create_tmp_file('abc.cpp')
        self.create_tmp_file('src/def.cpp')
        self.create_tmp_file('src/ghi.cpp')
        self.create_tmp_build_dir('build')

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            finder = SourceFinder(project)

            self.assertEqual('abc.cpp', finder.find_file('abc.cpp').path)
            self.assertEqual('src/def.cpp', finder.find_file('src/def.cpp').path)

            with self.assertRaisesRegex(Error, 'src'):
                _ = finder.find_file('src')

    def test_find_buildable_files(self):
        self.create_tmp_build_dir('build', comp_db=[
            {
                'directory': self.tmp_path('build'),
                'command': 'c++ -o abc.o -c ../abc.cpp',
                'file': '../abc.cpp'
            },
            {
                'directory': self.tmp_path('build'),
                'command': 'c++ -o ghi.o -c ../ghi.cpp',
                'file': '../ghi.cpp'
            }
        ])
        for path in ['abc.cpp', 'abc.h', 'def.cpp', 'def.h', 'ghi.cpp', 'ghi.h']:
            self.create_tmp_file(path)

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            finder = SourceFinder(project)

            self._assert_paths(['abc.cpp', 'ghi.cpp'], finder.find_buildable_files())

    def test_source_path_does_not_exist(self):
        self.create_tmp_file('exists.cpp')
        self.create_tmp_file('dir_exists/exists.cpp')
        self.create_tmp_build_dir('build')

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            finder = SourceFinder(project)

            with self.assertRaisesRegex(Error, 'does_not_exist.cpp'):
                finder.find_files(['does_not_exist.cpp'])

            with self.assertRaisesRegex(Error, 'does_not_exist.cpp'):
                finder.find_files(['exists.cpp, dir_exists', 'does_not_exist.cpp'])

            with self.assertRaisesRegex(Error, 'dir_does_not_exist'):
                finder.find_files(['exists.cpp', 'dir_exists', 'dir_does_not_exist'])

    def test_config_source_paths(self):
        self.create_tmp_file('abc/def.cpp')
        self.create_tmp_file('ghi/jkl.cpp')
        self.create_tmp_file('mno/pqr.cpp')
        self.create_tmp_build_dir('build')

        self.create_tmp_config('.', {'source_paths': ['abc', 'ghi']})

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            finder = SourceFinder(project)
            self._assert_paths(['abc/def.cpp', 'ghi/jkl.cpp'], finder.find_files())
            self._assert_paths(['abc/def.cpp'], finder.find_files(['abc']))

        self.create_tmp_config('.', {'source_paths': ['abc', 'does_not_exist']})

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            with self.assertRaisesRegex(Error, 'does_not_exist'):
                _ = SourceFinder(project).find_files()

    def test_config_exclude_regex(self):
        self.create_tmp_file('src/abc.cpp')
        self.create_tmp_file('src/def_skip.cpp')
        self.create_tmp_file('src/ghi.cpp')
        self.create_tmp_file('src/skip_jkl.cpp')
        self.create_tmp_file('src/dir_to_skip/mno.cpp')
        self.create_tmp_build_dir('build')

        self.create_tmp_config('.', {'source_exclude': '.*skip.*'})

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            finder = SourceFinder(project)
            self._assert_paths(['src/abc.cpp', 'src/ghi.cpp'], finder.find_files())

    def test_build_path_ignored(self):
        self.create_tmp_file('abc.cpp')
        self.create_tmp_file('def.cpp')
        self.create_tmp_build_dir('build')
        self.create_tmp_file('build/generated.cpp')

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            self._assert_paths(['abc.cpp', 'def.cpp'], SourceFinder(project).find_files())

    def test_build_path_same_as_project_path_not_ignored(self):
        # If build system allows build path to be the same as project path, and user decides to do
        # this, there is nothing we can do to automatically ignore generated sources in the build
        # directory. Make sure that source is still found so check that excludes it does not exclude
        # everything. Up to user to not do this if it causes trouble.
        self.create_tmp_file('abc.cpp')
        self.create_tmp_file('def.cpp')
        self.create_tmp_build_dir('.')
        self.create_tmp_file('generated.cpp')

        with self.cd_tmp_dir():
            project = Project('.', '.')
            self._assert_paths(['abc.cpp', 'def.cpp', 'generated.cpp'],
                               SourceFinder(project).find_files())
