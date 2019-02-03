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

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import paths


class FindProjectPathTestCase(TestCaseWithTmpDir):
    def test_dir_does_not_exist(self) -> None:
        self.create_tmp_dir('foo')

        with self.cd_tmp_dir():
            with self.assertRaises(paths.Error):
                paths.find_project_path('does_not_exist')

            with self.assertRaises(paths.Error):
                paths.find_project_path('foo/does_not_exist')

    def test_empty_dir(self) -> None:
        self.create_tmp_dir('empty')

        with self.cd_tmp_dir():
            with self.assertRaises(paths.Error):
                paths.find_project_path('empty')

    def test_relative_outside(self) -> None:
        self.create_tmp_file('foo/.sork')
        self.create_tmp_file('foo/bar/baz.cpp')

        with self.cd_tmp_dir():
            self.assertEqual('foo', paths.find_project_path('foo'))
            self.assertEqual('foo', paths.find_project_path('foo/bar'))
            self.assertEqual('foo', paths.find_project_path('foo/bar/baz.cpp'))

        self.create_tmp_dir('qux')

        with self.cd_tmp_dir('qux'):
            self.assertEqual('../foo', paths.find_project_path('../foo'))
            self.assertEqual('../foo', paths.find_project_path('../foo/bar'))
            self.assertEqual('../foo', paths.find_project_path('../foo/bar/baz.cpp'))

    def test_relative_inside(self) -> None:
        self.create_tmp_file('foo/.sork')
        self.create_tmp_file('foo/bar/baz.cpp')

        with self.cd_tmp_dir('foo'):
            self.assertEqual('.', paths.find_project_path('.'))
            self.assertEqual('.', paths.find_project_path('bar'))
            self.assertEqual('.', paths.find_project_path('bar/baz.cpp'))

        with self.cd_tmp_dir('foo/bar'):
            self.assertEqual('..', paths.find_project_path('.'))
            self.assertEqual('..', paths.find_project_path('..'))
            self.assertEqual('..', paths.find_project_path('baz.cpp'))

    def test_no_dot_sork_only_dot_git(self) -> None:
        self.create_tmp_dir('foo/.git')
        self.create_tmp_file('foo/bar/baz.cpp')

        with self.cd_tmp_dir():
            self.assertEqual('foo', paths.find_project_path('foo'))
            self.assertEqual('foo', paths.find_project_path('foo/bar'))
            self.assertEqual('foo', paths.find_project_path('foo/bar/baz.cpp'))


class FindBuildPathTestCase(TestCaseWithTmpDir):
    def test_no_build_dir_exists(self) -> None:
        self.create_tmp_file('foo/bar/baz.cpp')

        with self.cd_tmp_dir():
            with self.assertRaises(paths.Error):
                paths.find_build_path('foo')

    def test_in_project_root(self) -> None:
        self.create_tmp_file('foo/bar/baz.cpp')
        self.create_tmp_build_dir('foo/build')

        self.create_tmp_file('qux/bar/baz.cpp')
        self.create_tmp_build_dir('qux/build_release')

        with self.cd_tmp_dir():
            self.assertEqual('foo/build', paths.find_build_path('foo'))
            self.assertEqual('qux/build_release', paths.find_build_path('qux'))

        with self.cd_tmp_dir('foo'):
            self.assertEqual('build', paths.find_build_path('.'))

        with self.cd_tmp_dir('foo/bar'):
            self.assertEqual('../build', paths.find_build_path('..'))

        with self.cd_tmp_dir('qux'):
            self.assertEqual('build_release', paths.find_build_path('.'))

        with self.cd_tmp_dir('qux/bar'):
            self.assertEqual('../build_release', paths.find_build_path('..'))

    def test_in_same_dir_as_project_dir(self) -> None:
        self.create_tmp_file('foo/bar/baz.cpp')
        self.create_tmp_build_dir('foo-build')

        self.create_tmp_file('qux/bar/baz.cpp')
        self.create_tmp_build_dir('qux-build_release')

        with self.cd_tmp_dir():
            self.assertEqual('foo-build', paths.find_build_path('foo'))
            self.assertEqual('qux-build_release', paths.find_build_path('qux'))

        with self.cd_tmp_dir('foo'):
            self.assertEqual('../foo-build', paths.find_build_path('.'))

        with self.cd_tmp_dir('foo/bar'):
            self.assertEqual('../../foo-build', paths.find_build_path('..'))

        with self.cd_tmp_dir('qux'):
            self.assertEqual('../qux-build_release', paths.find_build_path('.'))

        with self.cd_tmp_dir('qux/bar'):
            self.assertEqual('../../qux-build_release', paths.find_build_path('..'))

    def test_build_subdir_in_same_dir_as_project(self) -> None:
        self.create_tmp_file('foo/bar/baz.cpp')
        self.create_tmp_build_dir('build/foo')

        self.create_tmp_file('qux/bar/baz.cpp')
        self.create_tmp_build_dir('build/qux_release')

        with self.cd_tmp_dir():
            self.assertEqual('build/foo', paths.find_build_path('foo'))
            self.assertEqual('build/qux_release', paths.find_build_path('qux'))

        with self.cd_tmp_dir('foo'):
            self.assertEqual('../build/foo', paths.find_build_path('.'))

        with self.cd_tmp_dir('foo/bar'):
            self.assertEqual('../../build/foo', paths.find_build_path('..'))

        with self.cd_tmp_dir('qux'):
            self.assertEqual('../build/qux_release', paths.find_build_path('.'))

        with self.cd_tmp_dir('qux/bar'):
            self.assertEqual('../../build/qux_release', paths.find_build_path('..'))

    def test_build_dash_dir_in_same_dir_as_project(self) -> None:
        self.create_tmp_file('foo/bar/baz.cpp')
        self.create_tmp_build_dir('build-foo')

        self.create_tmp_file('qux/bar/baz.cpp')
        self.create_tmp_build_dir('build-qux_release')

        with self.cd_tmp_dir():
            self.assertEqual('build-foo', paths.find_build_path('foo'))
            self.assertEqual('build-qux_release', paths.find_build_path('qux'))

        with self.cd_tmp_dir('foo'):
            self.assertEqual('../build-foo', paths.find_build_path('.'))

        with self.cd_tmp_dir('foo/bar'):
            self.assertEqual('../../build-foo', paths.find_build_path('..'))

        with self.cd_tmp_dir('qux'):
            self.assertEqual('../build-qux_release', paths.find_build_path('.'))

        with self.cd_tmp_dir('qux/bar'):
            self.assertEqual('../../build-qux_release', paths.find_build_path('..'))

    def test_multiple_build_paths(self) -> None:
        self.create_tmp_file('foo/bar/baz.cpp')
        self.create_tmp_build_dir('foo/build_debug')
        self.create_tmp_build_dir('foo/build_release')

        with self.cd_tmp_dir():
            with self.assertRaisesRegex(paths.Error, 'foo/build_'):
                paths.find_build_path('foo')


class NormalizePathTestCase(TestCaseWithTmpDir):
    def test_normalize_path(self) -> None:
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_dir('foo-build')

        with self.cd_tmp_dir():
            project_path = 'foo'
            self.assertEqual('.', paths.normalize_path(project_path, 'foo'))
            self.assertEqual('src', paths.normalize_path(project_path, 'foo/src'))
            self.assertEqual('src/bar.cpp', paths.normalize_path(project_path, 'foo/src/bar.cpp'))
            self.assertEqual('../foo-build', paths.normalize_path(project_path, 'foo-build'))

        with self.cd_tmp_dir('foo'):
            project_path = '.'
            self.assertEqual('.', paths.normalize_path(project_path, '.'))
            self.assertEqual('src', paths.normalize_path(project_path, 'src'))
            self.assertEqual('src/bar.cpp', paths.normalize_path(project_path, 'src/bar.cpp'))
            self.assertEqual('../foo-build', paths.normalize_path(project_path, '../foo-build'))

        with self.cd_tmp_dir('foo-build'):
            project_path = '../foo'
            self.assertEqual('.', paths.normalize_path(project_path, '../foo'))
            self.assertEqual('src', paths.normalize_path(project_path, '../foo/src'))
            self.assertEqual('src/bar.cpp', paths.normalize_path(project_path,
                                                                 '../foo/src/bar.cpp'))
            self.assertEqual('../foo-build', paths.normalize_path(project_path, '.'))

        with self.cd_tmp_dir('foo/src'):
            project_path = '..'
            self.assertEqual('.', paths.normalize_path(project_path, '..'))
            self.assertEqual('src', paths.normalize_path(project_path, '.'))
            self.assertEqual('src/bar.cpp', paths.normalize_path(project_path, 'bar.cpp'))
            self.assertEqual('../foo-build', paths.normalize_path(project_path, '../../foo-build'))

    def test_normalize_path_absolute(self) -> None:
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

        project_path = self.tmp_path('foo')
        self.assertEqual('.', paths.normalize_path(project_path, self.tmp_path('foo')))
        self.assertEqual('src', paths.normalize_path(project_path, self.tmp_path('foo/src')))
        self.assertEqual('src/bar.cpp', paths.normalize_path(project_path,
                                                             self.tmp_path('foo/src/bar.cpp')))
        self.assertEqual('../foo-build', paths.normalize_path(project_path,
                                                              self.tmp_path('foo-build')))

    def test_normalize_paths(self) -> None:
        self.create_tmp_file('foo/include/bar.h')
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

        norm_paths = ['.', 'include', 'include/bar.h', 'src', 'src/bar.cpp']
        norm_filter_proj_paths = ['include', 'include/bar.h', 'src', 'src/bar.cpp']

        with self.cd_tmp_dir():
            project_path = 'foo'
            test_paths = ['foo', 'foo/include', 'foo/include/bar.h', 'foo/src', 'foo/src/bar.cpp']
            self.assertEqual(norm_paths, paths.normalize_paths(project_path, test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             paths.normalize_paths(project_path,
                                                   test_paths,
                                                   filter_project_path=True))

        with self.cd_tmp_dir('foo'):
            project_path = '.'
            test_paths = ['.', 'include', 'include/bar.h', 'src', 'src/bar.cpp']
            self.assertEqual(norm_paths, paths.normalize_paths(project_path, test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             paths.normalize_paths(project_path,
                                                   test_paths,
                                                   filter_project_path=True))

        with self.cd_tmp_dir('foo-build'):
            project_path = '../foo'
            test_paths = ['../foo', '../foo/include', '../foo/include/bar.h', '../foo/src',
                          '../foo/src/bar.cpp']
            self.assertEqual(norm_paths, paths.normalize_paths(project_path, test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             paths.normalize_paths(project_path,
                                                   test_paths,
                                                   filter_project_path=True))

        with self.cd_tmp_dir('foo/src'):
            project_path = '..'
            test_paths = ['..', '../include', '../include/bar.h', '.', 'bar.cpp']
            self.assertEqual(norm_paths, paths.normalize_paths(project_path, test_paths))
            self.assertEqual(norm_filter_proj_paths,
                             paths.normalize_paths(project_path,
                                                   test_paths,
                                                   filter_project_path=True))

    def test_normalize_paths_absolute(self) -> None:
        self.create_tmp_file('foo/src/bar.cpp')
        self.create_tmp_build_dir('foo-build')

        project_path = self.tmp_path('foo')
        test_paths = [self.tmp_path(p) for p in ['foo', 'foo/src', 'foo/src/bar.cpp']]

        self.assertEqual(['.', 'src', 'src/bar.cpp'],
                         paths.normalize_paths(project_path, test_paths))
        self.assertEqual(['src', 'src/bar.cpp'],
                         paths.normalize_paths(project_path, test_paths, filter_project_path=True))
