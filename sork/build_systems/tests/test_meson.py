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

from sork.tests import popen_mock
from sork.tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import meson


class IsMesonBuildPathTestCase(TestCaseWithTmpDir):
    def test_is_a_meson_build_path(self):
        self.create_tmp_dir('build/meson-private')

        with self.cd_tmp_dir():
            self.assertTrue(meson.is_meson_build_path('build'))

    def test_is_not_a_meson_build_path(self):
        self.create_tmp_dir('build')
        self.create_tmp_file('build2/garbage.txt')

        with self.cd_tmp_dir():
            self.assertFalse(meson.is_meson_build_path('build'))
            self.assertFalse(meson.is_meson_build_path('build2'))
            self.assertFalse(meson.is_meson_build_path('does_not_exist'))


class MesonDependenciesTestCase(TestCaseWithTmpDir):
    def test_valid_json(self):
        with popen_mock.patch(stdout=[
            {'name': 'libfoo',
             'compile_args': ['-I/usr/include/foo'],
             'link_args': []},
            {'name': 'libbar',
             'compile_args': ['-I/usr/include/bar/1', '-isystem/usr/include/bar/2', '-iquotesrc'],
             'link_args': ['-lbar']},
            {'name': 'baz',
             'compile_args': ['-pthread'],
             'link_args': ['']}]):
            deps = meson.dependencies('build')

        self.assertEqual(3, len(deps))

        self.assertEqual('libfoo', deps[0].name)
        self.assertEqual(['/usr/include/foo'], deps[0].include_paths)

        self.assertEqual('libbar', deps[1].name)
        self.assertEqual(['/usr/include/bar/1', '/usr/include/bar/2', 'src'], deps[1].include_paths)

        self.assertEqual('baz', deps[2].name)
        self.assertEqual([], deps[2].include_paths)

    def test_invalid_json(self):
        with popen_mock.patch(stdout='garbage'):
            with self.assertRaises(meson.Error):
                _ = meson.dependencies('build')

    def test_error_return_code(self):
        with popen_mock.patch(stdout=[], stderr='foo', returncode=1):
            with self.assertRaisesRegex(meson.Error, 'mesonintrospect.*foo'):
                _ = meson.dependencies('build')

    def test_no_deps(self):
        with popen_mock.patch(stdout=[]):
            deps = meson.dependencies('build')

        self.assertEqual(0, len(deps))
