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

import contextlib
import json
import os
import tempfile
import unittest

from typing import Any, Dict, Iterator, List, Optional, Union

from .. import paths
from ..config import Config


class TestCaseWithTmpDir(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

    def tmp_path(self, path: str) -> str:
        if path.startswith(self.tmp_dir.name):
            return path
        return os.path.join(self.tmp_dir.name, path)

    def create_tmp_dir(self, dir_path: str) -> None:
        os.makedirs(self.tmp_path(dir_path), exist_ok=True)

    def create_tmp_file(self,
                        file_path: str,
                        content: Optional[Union[str, List[str]]] = None) -> None:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            self.create_tmp_dir(dir_path)

        if isinstance(content, list):
            content = '\n'.join(content)

        with open(self.tmp_path(file_path), 'w') as file:
            file.write(content if content else '')

    def create_tmp_config(self, project_path: str, config: Config) -> None:
        self.create_tmp_file(os.path.join(project_path, paths.DOT_SORK_PATH),
                             json.dumps(config))

    @staticmethod
    def comp_db_path(build_path: str) -> str:
        return os.path.join(build_path, paths.COMPILE_COMMANDS_JSON_PATH)

    def create_tmp_comp_db(self,
                           build_path: str,
                           content: Union[str, List[Dict[str, Any]]]) -> None:
        if not isinstance(content, str):
            content = json.dumps(content)

        self.create_tmp_file(self.comp_db_path(build_path), content)

    def create_tmp_build_dir(self,
                             build_path: str,
                             comp_db: Optional[List[Dict[str, Any]]] = None) -> None:
        self.create_tmp_comp_db(build_path, comp_db or '[]')

    @contextlib.contextmanager
    def cd_tmp_dir(self, sub_dir: Optional[str] = None) -> Iterator[None]:
        orig_work_dir = os.getcwd()
        os.chdir(self.tmp_path(sub_dir) if sub_dir else self.tmp_dir.name)
        try:
            yield
        finally:
            os.chdir(orig_work_dir)
