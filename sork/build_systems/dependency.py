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

import logging

from typing import List


class Dependency:
    def __init__(self, name: str, include_paths: List[str]) -> None:
        self.name = name
        self.include_paths = include_paths


def find_dependencies(build_path: str) -> List[Dependency]:
    # Importing here since Python cannot cope with "-> List[Dependency]" annotation at top level in
    # cmake and meson modules if they are placed before class Dependency above.
    from . import cmake
    from . import meson

    if meson.is_meson_build_path(build_path):
        return meson.dependencies(build_path)

    if cmake.is_cmake_build_path(build_path):
        return cmake.dependencies(build_path)

    logging.warning('Unable to extract dependencies from build system.')

    return []
