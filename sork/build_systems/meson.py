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

import json
import os
import shutil
import subprocess

from .. import error


def is_meson_build_path(build_path):
    return os.path.exists(os.path.join(build_path, 'meson-private'))


def _introspect(args):
    mesonintrospect = shutil.which('mesonintrospect')

    if not mesonintrospect:
        raise error.Error('Unable to locate mesonintrospect')

    with subprocess.Popen([mesonintrospect] + args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise error.Error('mesonintrospect failed: {}'.format(stderr))

    return stdout


def dependencies(build_path):
    json_str = _introspect(['--dependencies', build_path])

    try:
        json_object = json.loads(json_str)
    except json.JSONDecodeError as exception:
        raise error.Error('Failed to decode Meson introspection data: {}', exception)

    if not isinstance(json_object, dict):
        raise error.Error('Meson introspection JSON for dependencies is not an object.')

    # dict() only needed to unconfuse pylint when using items() on return value. Thinks return
    # value from json.loads() is a bool. Even with isinstance check above. Adding a "-> dict"
    # type hint to function signature does not help either. *sigh*
    return dict(json_object)
