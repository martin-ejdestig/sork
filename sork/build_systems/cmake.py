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

import os
import re

from typing import Dict, List

from .dependency import Dependency


def _cmake_cache_path(build_path: str) -> str:
    return os.path.join(build_path, 'CMakeCache.txt')


def is_cmake_build_path(build_path: str) -> bool:
    return os.path.exists(_cmake_cache_path(build_path))


def _internal_cache_variables(build_path: str) -> Dict[str, str]:
    variables = {}

    with open(_cmake_cache_path(build_path)) as file:
        cache = file.read()
        for line in cache.splitlines():
            split = re.split(':INTERNAL=', line)
            if len(split) == 2:
                variables[split[0]] = split[1]

    return variables


def dependencies(build_path: str) -> List[Dependency]:
    deps = []

    # Currently only catches pkg-config dependencies for sure. Other CMake modules may do
    # whatever they want, not possible to catch them all. If a more structured way to query
    # CMake ever materializes (CMake 3.7 does not have any AFAIK), use that instead.
    cache_vars = _internal_cache_variables(build_path)

    for name, value in cache_vars.items():
        if name.endswith('_FOUND') and value == '1':
            dep_name = name[:-len('_FOUND')]
            include_dirs_value = cache_vars.get(dep_name + '_INCLUDE_DIRS')
            include_paths = include_dirs_value.split(';') if include_dirs_value else []
            deps.append(Dependency(dep_name, include_paths))

    return deps
