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

import logging

from ...tests import popen_mock
from ...tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import dependencies


class DependenciesFindTestCase(TestCaseWithTmpDir):
    def test_meson(self):
        self.create_tmp_dir('build/meson-private')

        with self.cd_tmp_dir():
            with popen_mock.patch(stdout=[
                {'name': 'libfoo',
                 'compile_args': ['-I/usr/include/foo'],
                 'link_args': []}]):
                deps = dependencies.find('build')

        self.assertEqual(1, len(deps))
        self.assertEqual('libfoo', deps[0].name)
        self.assertEqual(['/usr/include/foo'], deps[0].include_paths)

    def test_cmake(self):
        self.create_tmp_file('build/CMakeCache.txt',
                             'LIBFOO_FOUND:INTERNAL=1\n'
                             'LIBFOO_INCLUDE_DIRS:INTERNAL=/usr/include/foo\n')

        with self.cd_tmp_dir():
            deps = dependencies.find('build')

        self.assertEqual(1, len(deps))
        self.assertEqual('LIBFOO', deps[0].name)
        self.assertEqual(['/usr/include/foo'], deps[0].include_paths)

    def test_unsopported_build_system(self):
        self.create_tmp_dir('build')

        with self.cd_tmp_dir():
            with self.assertLogs(level=logging.WARNING):
                deps = dependencies.find('build')

        self.assertEqual([], deps)
