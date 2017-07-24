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

import re
import sys

from typing import List, TextIO

from . import cmake
from . import meson


class Dependency:
    def __init__(self, name: str, include_paths: List[str]) -> None:
        self.name = name
        self.include_paths = include_paths


class DependencyFinder:
    def __init__(self, build_path: str, error_output: TextIO = sys.stderr) -> None:
        self._build_path = build_path
        self._error_output = error_output

    def find(self) -> List[Dependency]:
        if meson.is_meson_build_path(self._build_path):
            return self._meson_dependencies()

        if cmake.is_cmake_build_path(self._build_path):
            return self._cmake_dependencies()

        self._log_warning('Unable to extract dependencies from build system.')

        return []

    def _meson_dependencies(self) -> List[Dependency]:
        deps = meson.dependencies(self._build_path)

        return [Dependency(dep['name'], self._include_paths_from_args(dep['compile_args']))
                for dep in deps]

    def _cmake_dependencies(self) -> List[Dependency]:
        deps = []

        # Currently only catches pkg-config dependencies for sure. Other CMake modules may do
        # whatever they want, not possible to catch them all. If a more structured way to query
        # CMake ever materializes (CMake 3.7 does not have any AFAIK), use that instead.
        cache_vars = cmake.internal_cache_variables(self._build_path)

        for name, value in cache_vars.items():
            if name.endswith('_FOUND') and value == '1':
                dep_name = name[:-len('_FOUND')]
                include_dirs_value = cache_vars.get(dep_name + '_INCLUDE_DIRS')
                include_paths = include_dirs_value.split(';') if include_dirs_value else []
                deps.append(Dependency(dep_name, include_paths))

        return deps

    def _log_warning(self, message: str):
        print('Warning: {}'.format(message), file=self._error_output)

    @staticmethod
    def _include_paths_from_args(args: List[str]) -> List[str]:
        paths = []

        for arg in args:
            match = re.match('^(-I|-isystem|-iquote)(.+)', arg)
            if match:
                paths.append(match.group(2))

        return paths
