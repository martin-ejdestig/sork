# This file is part of Sork.
#
# Copyright (C) 2016-2017 Martin Ejdestig <marejde@gmail.com>
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

import itertools
import os

from typing import Dict, List, Optional

from . import compilation_database
from . import config
from . import error
from .build_systems import dependency


_NORMALIZED_PROJECT_PATH = os.path.curdir

_DOT_SORK_PATH = '.sork'
_DOT_PATHS_IN_PROJECT_ROOT = ['.git', _DOT_SORK_PATH]


def _is_project_path(path: str) -> bool:
    return any(os.path.exists(os.path.join(path, dp))
               for dp in _DOT_PATHS_IN_PROJECT_ROOT)


def _find_project_path(path: str) -> str:
    if os.path.isfile(path):
        path = os.path.dirname(path)

    while not _is_project_path(path):
        parent_path = os.path.relpath(os.path.join(path, os.path.pardir))

        if path == parent_path:
            raise error.Error('Unable to determine project root path. '
                              'Currently looking for: {}'
                              .format(', '.join(_DOT_PATHS_IN_PROJECT_ROOT)))

        path = parent_path

    return path


class Environment:
    def __init__(self, path_in_project: str, build_path: Optional[str] = None) -> None:
        self.project_path = _find_project_path(path_in_project)
        self.build_path = build_path

        self.config = config.create(os.path.join(self.project_path, _DOT_SORK_PATH))

        self.compilation_database = compilation_database.CompilationDatabase(self.project_path,
                                                                             self.build_path)
        if not self.build_path:
            self.build_path = os.path.dirname(self.compilation_database.path)

        self.dependencies = dependency.DependencyFinder(self.build_path).find()

    def normalize_path(self, path: str) -> str:
        return os.path.normpath(os.path.relpath(path, start=self.project_path))

    def normalize_paths(self, paths: List[str], filter_project_path: bool = False) -> List[str]:
        normalized_paths = [self.normalize_path(path) for path in paths]
        if filter_project_path:
            normalized_paths = [path for path in normalized_paths
                                if path != _NORMALIZED_PROJECT_PATH]
        return normalized_paths

    def command_env_vars(self) -> Dict[str, str]:
        env = os.environ.copy()

        include_paths = self._dependency_include_paths()
        if include_paths:
            self._env_append_paths(env, 'C_INCLUDE_PATH', include_paths)
            self._env_append_paths(env, 'CPLUS_INCLUDE_PATH', include_paths)

        return env

    def _dependency_include_paths(self) -> List[str]:
        paths = itertools.chain.from_iterable([dep.include_paths for dep in self.dependencies])
        return sorted(set(paths))

    @staticmethod
    def _env_append_paths(env: Dict[str, str], name: str, paths: List[str]):
        orig_value = env.get(name)
        env[name] = os.pathsep.join(([orig_value] if orig_value else []) + paths)
