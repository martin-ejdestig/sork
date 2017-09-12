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

from sork.tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import cmake


class IsCMakeBuildPathTestCase(TestCaseWithTmpDir):
    def test_is_a_cmake_build_path(self):
        self.create_tmp_file('build/CMakeCache.txt')

        with self.cd_tmp_dir():
            self.assertTrue(cmake.is_cmake_build_path('build'))

    def test_is_not_a_cmake_build_path(self):
        self.create_tmp_dir('build')
        self.create_tmp_file('build2/garbage.txt')

        with self.cd_tmp_dir():
            self.assertFalse(cmake.is_cmake_build_path('build'))
            self.assertFalse(cmake.is_cmake_build_path('build2'))
            self.assertFalse(cmake.is_cmake_build_path('does_not_exist'))


class CMakeDependenciesTestCase(TestCaseWithTmpDir):
    def test_cmake_cache_txt_does_not_exist(self):
        with self.cd_tmp_dir():
            with self.assertRaisesRegex(FileNotFoundError, 'build/CMakeCache.txt'):
                cmake.dependencies('build')

    def test_cmake_cache_txt_contains_garbage(self):
        self.create_tmp_file('build/CMakeCache.txt', 'garbage')

        with self.cd_tmp_dir():
            self.assertEqual([], cmake.dependencies('build'))

    def test_valid_cmake_cache_txt(self):
        self.create_tmp_file('build/CMakeCache.txt',
                             '# A comment\n'
                             '// Another comment\n'
                             'LIBFOO_FOUND:INTERNAL=1\n'
                             'LIBFOO_INCLUDE_DIRS:INTERNAL=/usr/include/foo\n'
                             'LIBBAR_FOUND:INTERNAL=1\n'
                             'LIBBAR_INCLUDE_DIRS:INTERNAL=/usr/include/bar/1;/usr/include/bar/2\n'
                             'LIBBAZ_FOUND:INTERNAL=0\n'
                             'QUX_FOUND:INTERNAL=1\n'
                             'QUX_INCLUDE_DIRS:INTERNAL=\n')

        with self.cd_tmp_dir():
            deps = cmake.dependencies('build')

        self.assertEqual(3, len(deps))

        self.assertEqual('LIBFOO', deps[0].name)
        self.assertEqual(['/usr/include/foo'], deps[0].include_paths)

        self.assertEqual('LIBBAR', deps[1].name)
        self.assertEqual(['/usr/include/bar/1', '/usr/include/bar/2'], deps[1].include_paths)

        self.assertEqual('QUX', deps[2].name)
        self.assertEqual([], deps[2].include_paths)
