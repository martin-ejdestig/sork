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
import json
import os
import tempfile
import unittest

from typing import Any, Dict, List, Optional, Union

from .. import paths


class TmpDependency:
    def __init__(self, name: str, include_paths: List[str]) -> None:
        self.name = name
        self.include_paths = include_paths


# Used to create build dir with CMakeCache.txt since CMake currently is the
# easiest supported build system to simulate without mocking.
def _cmake_cache_content(dependencies: List[TmpDependency]) -> str:
    content = ''

    for dep in dependencies:
        content += '{}_FOUND:INTERNAL=1\n'.format(dep.name)
        content += '{}_INCLUDE_DIRS:INTERNAL={}\n'.format(dep.name, ';'.join(dep.include_paths))

    return content


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

    @staticmethod
    def comp_db_path(build_path: str) -> str:
        return os.path.join(build_path, paths.COMPILE_COMMANDS_JSON_PATH)

    def create_tmp_comp_db(self,
                           build_path: str,
                           content: Union[None, str, List[Dict[str, Any]]] = None):
        if content is None:
            content = ''
        elif not isinstance(content, str):
            content = json.dumps(content)

        self.create_tmp_file(self.comp_db_path(build_path), content)

    def create_tmp_build_dir(self,
                             build_path: str,
                             dependencies: Optional[List[TmpDependency]] = None):
        self.create_tmp_comp_db(build_path, [])

        self.create_tmp_file(os.path.join(build_path, 'CMakeCache.txt'),
                             _cmake_cache_content(dependencies) if dependencies else None)

    @contextlib.contextmanager
    def cd_tmp_dir(self, sub_dir: Optional[str] = None):
        orig_work_dir = os.getcwd()
        os.chdir(self.tmp_path(sub_dir) if sub_dir else self.tmp_dir.name)
        try:
            yield
        finally:
            os.chdir(orig_work_dir)
