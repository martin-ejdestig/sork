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

import os

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import paths
from ..project import Project


class ProjectTestCase(TestCaseWithTmpDir):
    def _create_project(self, path: str, build_path: str):
        self.create_tmp_dir(path)

        self.create_tmp_file(os.path.join(build_path, paths.COMPILE_COMMANDS_JSON_PATH), '[]')

        # Create a CMakeCache.txt since CMake currently is the easiest supported
        # build system to simulate without mocking.
        self.create_tmp_file(os.path.join(build_path, 'CMakeCache.txt'))

    def test_environment(self):
        # TODO
        pass

    def test_normalize_path(self):
        self._create_project('foo', 'foo-build')
        self.create_tmp_file('foo/src/bar.cpp')

        with self.cd_tmp_dir():
            project = Project('foo', 'foo-build')
            self.assertEqual('.', project.normalize_path('foo'))
            self.assertEqual('src', project.normalize_path('foo/src'))
            self.assertEqual('src/bar.cpp', project.normalize_path('foo/src/bar.cpp'))
            self.assertEqual('../foo-build', project.normalize_path('foo-build'))

        with self.cd_tmp_dir('foo'):
            project = Project('.', '../foo-build')
            self.assertEqual('.', project.normalize_path('.'))
            self.assertEqual('src', project.normalize_path('src'))
            self.assertEqual('src/bar.cpp', project.normalize_path('src/bar.cpp'))
            self.assertEqual('../foo-build', project.normalize_path('../foo-build'))

        with self.cd_tmp_dir('foo-build'):
            project = Project('../foo', '.')
            self.assertEqual('.', project.normalize_path('../foo'))
            self.assertEqual('src', project.normalize_path('../foo/src'))
            self.assertEqual('src/bar.cpp', project.normalize_path('../foo/src/bar.cpp'))
            self.assertEqual('../foo-build', project.normalize_path('.'))

        with self.cd_tmp_dir('foo/src'):
            project = Project('..', '../../foo-build')
            self.assertEqual('.', project.normalize_path('..'))
            self.assertEqual('src', project.normalize_path('.'))
            self.assertEqual('src/bar.cpp', project.normalize_path('bar.cpp'))
            self.assertEqual('../foo-build', project.normalize_path('../../foo-build'))

    def test_normalize_path_absolute(self):
        self._create_project('foo', 'foo-build')
        self.create_tmp_file('foo/src/bar.cpp')

        project = Project(self.tmp_path('foo'), self.tmp_path('foo-build'))
        self.assertEqual('.', project.normalize_path(self.tmp_path('foo')))
        self.assertEqual('src', project.normalize_path(self.tmp_path('foo/src')))
        self.assertEqual('src/bar.cpp', project.normalize_path(self.tmp_path('foo/src/bar.cpp')))
        self.assertEqual('../foo-build', project.normalize_path(self.tmp_path('foo-build')))

    def test_normalize_paths(self):
        self._create_project('foo', 'foo-build')
        self.create_tmp_file('foo/include/bar.h')
        self.create_tmp_file('foo/src/bar.cpp')

        norm_paths = ['.', 'include', 'include/bar.h', 'src', 'src/bar.cpp']
        norm_filter_proj_paths = ['include', 'include/bar.h', 'src', 'src/bar.cpp']

        with self.cd_tmp_dir():
            project = Project('foo', 'foo-build')
            test_paths = ['foo', 'foo/include', 'foo/include/bar.h', 'foo/src', 'foo/src/bar.cpp']
            self.assertEqual(norm_paths, project.normalize_paths(test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             project.normalize_paths(test_paths, filter_project_path=True))

        with self.cd_tmp_dir('foo'):
            project = Project('.', '../foo-build')
            test_paths = ['.', 'include', 'include/bar.h', 'src', 'src/bar.cpp']
            self.assertEqual(norm_paths, project.normalize_paths(test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             project.normalize_paths(test_paths, filter_project_path=True))

        with self.cd_tmp_dir('foo-build'):
            project = Project('../foo', '.')
            test_paths = ['../foo', '../foo/include', '../foo/include/bar.h', '../foo/src',
                          '../foo/src/bar.cpp']
            self.assertEqual(norm_paths, project.normalize_paths(test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             project.normalize_paths(test_paths, filter_project_path=True))

        with self.cd_tmp_dir('foo/src'):
            project = Project('..', '../../foo-build')
            test_paths = ['..', '../include', '../include/bar.h', '.', 'bar.cpp']
            self.assertEqual(norm_paths, project.normalize_paths(test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             project.normalize_paths(test_paths, filter_project_path=True))

    def test_normalize_paths_absolute(self):
        self._create_project('foo', 'foo-build')
        self.create_tmp_file('foo/src/bar.cpp')

        project = Project(self.tmp_path('foo'), self.tmp_path('foo-build'))
        test_paths = [self.tmp_path(p) for p in ['foo', 'foo/src', 'foo/src/bar.cpp']]

        self.assertEqual(['.', 'src', 'src/bar.cpp'], project.normalize_paths(test_paths))
        self.assertEqual(['src', 'src/bar.cpp'],
                         project.normalize_paths(test_paths, filter_project_path=True))
