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

from typing import List

from ...project import Project
from ...tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from .. import create


# TODO: A bit ugly that setup requires knowledge about certain checks' requirements on file
#       structure/configuration. Maybe create a couple of dummy checks here instead? Would require
#       changing create module to not have hardcoded list of available checks though and do not
#       really want that.
class CreateFromStringsTestCase(TestCaseWithTmpDir):
    def setUp(self) -> None:
        super().setUp()
        self.create_tmp_build_dir('build')
        self.create_tmp_config('.', {'checks.license_header': {'license': ['foo']}})
        self._project = Project(self.tmp_path('.'), self.tmp_path('build'))

    def _created_names(self, check_strings: List[str]) -> List[str]:
        return [check.name for check in create.from_strings(self._project, check_strings)]

    def test_none_creates_all(self) -> None:
        self.assertEqual(create.NAMES, self._created_names([]))

    def test_explicitly_enable(self) -> None:
        self.assertEqual(['include_guard'], self._created_names(['include_guard']))

        self.assertEqual(['clang-format', 'include_guard'],
                         self._created_names(['clang-format', 'include_guard']))

    def test_explicitly_disable(self) -> None:
        self.assertEqual([n for n in create.NAMES if not n == 'include_guard'],
                         self._created_names(['-include_guard']))

        self.assertEqual([n for n in create.NAMES if n not in ['clang-format', 'include_guard']],
                         self._created_names(['-clang-format', '-include_guard']))

    def test_regex(self) -> None:
        clang_names = [n for n in create.NAMES if n.startswith('clang')]
        clang_names_not_tidy = [n for n in clang_names if not n.endswith('tidy')]
        non_clang_names = [n for n in create.NAMES if n not in clang_names]

        self.assertEqual(create.NAMES, self._created_names(['.*']))

        self.assertEqual(clang_names, self._created_names(['clang.*']))
        self.assertEqual(non_clang_names, self._created_names(['-clang.*']))

        self.assertEqual(clang_names_not_tidy, self._created_names(['clang.*', '-.*tidy']))
        # TODO: Is this wanted behaviour? Modify to return same as above?
        self.assertEqual(create.NAMES, self._created_names(['-.*tidy', 'clang.*']))

    def test_no_checks_not_allowed(self) -> None:
        with self.assertRaisesRegex(create.Error, '-.*'):
            _ = self._created_names(['-.*'])

    def test_name_matches_nothing(self) -> None:
        with self.assertRaisesRegex(create.Error, 'invalid_name'):
            _ = self._created_names(['invalid_name'])

        with self.assertRaisesRegex(create.Error, '.*regex_that_matches_nothing.*'):
            _ = self._created_names(['.*regex_that_matches_nothing.*'])
