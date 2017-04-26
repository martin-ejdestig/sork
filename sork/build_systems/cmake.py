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

import os
import re


def _cmake_cache_path(build_path):
    return os.path.join(build_path, 'CMakeCache.txt')


def is_cmake_build_path(build_path):
    return os.path.exists(_cmake_cache_path(build_path))


def internal_cache_variables(build_path):
    variables = {}

    with open(_cmake_cache_path(build_path)) as file:
        cache = file.read()
        for line in cache.splitlines():
            split = re.split(':INTERNAL=', line)
            if len(split) == 2:
                variables[split[0]] = split[1]

    return variables
