# This file is part of Sork.
#
# Copyright (C) 2018 Martin Ejdestig <marejde@gmail.com>
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

from typing import Type

from ...project import Project
from ...source import SourceFile
from ...tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from ..check import Check


class CheckTestCase(TestCaseWithTmpDir):
    CHECK_CLASS: Type[Check]

    def setUp(self):
        super().setUp()
        self.create_tmp_build_dir('build')
        self._project = Project(self.tmp_path('.'), self.tmp_path('build'))
        self._check = self.CHECK_CLASS(self._project)

    def create_source(self, path: str, content: str) -> SourceFile:
        self.create_tmp_file(path, content)
        return SourceFile(path, self._project)
