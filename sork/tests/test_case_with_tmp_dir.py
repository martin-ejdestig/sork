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

import contextlib
import os
import tempfile
import unittest

from typing import Optional


class TestCaseWithTmpDir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

    def tmp_path(self, sub_path: str) -> str:
        return os.path.join(self.tmp_dir.name, sub_path)

    def create_tmp_dir(self, dir_path: str):
        os.makedirs(self.tmp_path(dir_path), exist_ok=True)

    def create_tmp_file(self, file_path: str, content: Optional[str] = None):
        dir_path = os.path.dirname(file_path)
        if dir_path:
            self.create_tmp_dir(dir_path)

        with open(self.tmp_path(file_path), 'w') as file:
            file.write(content if content else '')

    @contextlib.contextmanager
    def cd_tmp_dir(self, sub_dir: Optional[str] = None):
        orig_work_dir = os.getcwd()
        os.chdir(self.tmp_path(sub_dir) if sub_dir else self.tmp_dir.name)
        try:
            yield
        finally:
            os.chdir(orig_work_dir)
