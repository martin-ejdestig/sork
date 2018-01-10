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

import json
import os
import re
import subprocess

from typing import Any, List

from .dependency import Dependency

from .. import error


class Error(error.Error):
    pass


def is_meson_build_path(build_path: str) -> bool:
    return os.path.exists(os.path.join(build_path, 'meson-private'))


def _introspect(args: List[str]) -> Any:
    with subprocess.Popen(['mesonintrospect'] + args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Error('mesonintrospect failed: {}'.format(stderr))

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exception:
        raise Error('Failed to decode Meson introspection data: {}'.format(exception))


def _include_paths_from_args(args: List[str]) -> List[str]:
    paths = []

    for arg in args:
        match = re.match('^(-I|-isystem|-iquote)(.+)', arg)
        if match:
            paths.append(match.group(2))

    return paths


def dependencies(build_path: str) -> List[Dependency]:
    deps = _introspect(['--dependencies', build_path])

    return [Dependency(dep['name'], _include_paths_from_args(dep['compile_args']))
            for dep in deps]
