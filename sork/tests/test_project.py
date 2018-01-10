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

from .test_case_with_tmp_dir import TestCaseWithTmpDir, TmpDependency

from ..project import ENV_C_INCLUDE_PATH, ENV_CPLUS_INCLUDE_PATH, Project


class ProjectTestCase(TestCaseWithTmpDir):
    def test_environment_dependency_include_paths(self):
        self.create_tmp_build_dir('build', dependencies=[TmpDependency('dep1', ['/foo/include']),
                                                         TmpDependency('dep2', ['/bar/include',
                                                                                '/baz/include']),
                                                         TmpDependency('dep3', [])])

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            c_inc_paths = project.environment[ENV_C_INCLUDE_PATH]
            cplus_inc_paths = project.environment[ENV_CPLUS_INCLUDE_PATH]

        self.assertIn('/foo/include', c_inc_paths)
        self.assertIn('/foo/include', cplus_inc_paths)
        self.assertIn('/bar/include', c_inc_paths)
        self.assertIn('/bar/include', cplus_inc_paths)
        self.assertIn('/baz/include', c_inc_paths)
        self.assertIn('/baz/include', cplus_inc_paths)

    def test_normalize_path(self):
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

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
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

        project = Project(self.tmp_path('foo'), self.tmp_path('foo-build'))
        self.assertEqual('.', project.normalize_path(self.tmp_path('foo')))
        self.assertEqual('src', project.normalize_path(self.tmp_path('foo/src')))
        self.assertEqual('src/bar.cpp', project.normalize_path(self.tmp_path('foo/src/bar.cpp')))
        self.assertEqual('../foo-build', project.normalize_path(self.tmp_path('foo-build')))

    def test_normalize_paths(self):
        self.create_tmp_file('foo/include/bar.h')
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

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
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

        project = Project(self.tmp_path('foo'), self.tmp_path('foo-build'))
        test_paths = [self.tmp_path(p) for p in ['foo', 'foo/src', 'foo/src/bar.cpp']]

        self.assertEqual(['.', 'src', 'src/bar.cpp'], project.normalize_paths(test_paths))
        self.assertEqual(['src', 'src/bar.cpp'],
                         project.normalize_paths(test_paths, filter_project_path=True))
