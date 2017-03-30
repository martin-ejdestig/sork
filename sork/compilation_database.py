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

import collections
import glob
import itertools
import json
import os


COMPILE_COMMANDS_JSON_PATH = 'compile_commands.json'

CompileCommand = collections.namedtuple('CompileCommand', ['invokation', 'work_dir', 'file'])


class Error(Exception):
    pass


def _build_path_patterns(project_path, basename):
    pattern_dir_components = [
        ['*'],
        [os.path.pardir, basename + '*'],
        [os.path.pardir, 'build*', basename + '*'],
        [os.path.pardir, 'build-' + basename + '*']
    ]
    return [os.path.join(project_path, *cs) for cs in pattern_dir_components]


def _find_potential_paths(project_path):
    basename = os.path.basename(os.path.abspath(project_path))

    patterns = [os.path.join(pattern, COMPILE_COMMANDS_JSON_PATH)
                for pattern in _build_path_patterns(project_path, basename)]

    paths = itertools.chain.from_iterable([glob.glob(p) for p in patterns])

    return [os.path.dirname(os.path.normpath(path)) for path in paths]


def find_build_path(project_path):
    paths = _find_potential_paths(project_path)

    if not paths:
        raise Error('Unable to determine build path. Specify a path manually or '
                    'use one of the standard locations:\n{}'
                    .format('\n'.join(_build_path_patterns('path_to_project',
                                                           'name_of_project_directory'))))

    if len(paths) > 1:
        raise Error('Multiple build paths found, specify a path manually:\n{}'
                    .format('\n'.join(sorted(paths))))

    return paths[0]


def load_from_file(environment):
    commands = {}

    with open(os.path.join(environment.build_path, COMPILE_COMMANDS_JSON_PATH)) as file:
        for command in json.load(file):
            src_path = environment.normalize_path(os.path.join(command['directory'],
                                                               command['file']))
            commands[src_path] = CompileCommand(command['command'],
                                                command['directory'],
                                                command['file'])

    return commands
