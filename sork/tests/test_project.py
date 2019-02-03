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

from ..project import Project


class ProjectTestCase(TestCaseWithTmpDir):
    def test_create_from_empty_dir(self) -> None:
        self.create_tmp_dir('foo')
        self.create_tmp_build_dir('foo-build')

        with self.cd_tmp_dir():
            project = Project('foo', 'foo-build')
            self.assertEqual('foo', project.path)
            self.assertEqual('foo-build', project.build_path)
