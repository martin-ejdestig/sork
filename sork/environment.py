# This file is part of Sork.
#
# Copyright (C) 2016 Martin Ejdestig <marejde@gmail.com>
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

import glob
import itertools
import json
import os

from . import compilation_database


NORMALIZED_PROJECT_PATH = os.path.curdir

_DOT_SORK_PATH = '.sork'
_DOT_PATHS_IN_PROJECT_ROOT = ['.git', _DOT_SORK_PATH]


class Error(Exception):
    pass


def _is_project_path(path):
    return any(os.path.exists(os.path.join(path, dp))
               for dp in _DOT_PATHS_IN_PROJECT_ROOT)


def _find_project_path(path):
    while not _is_project_path(path):
        parent_path = os.path.relpath(os.path.join(path, os.path.pardir))

        if path == parent_path:
            raise Error('Unable to determine project root path. '
                        'Currently looking for: {}'
                        .format(', '.join(_DOT_PATHS_IN_PROJECT_ROOT)))

        path = parent_path

    return path


def _build_path_patterns(project_path, basename):
    pattern_dir_components = [
        ['*'],
        [os.path.pardir, basename + '*'],
        [os.path.pardir, 'build*', basename + '*']
    ]
    return [os.path.join(project_path, *cs) for cs in pattern_dir_components]


def _find_compile_commands_paths(project_path):
    basename = os.path.basename(os.path.abspath(project_path))

    patterns = [os.path.join(pattern, compilation_database.COMPILE_COMMANDS_JSON_PATH)
                for pattern in _build_path_patterns(project_path, basename)]

    paths = itertools.chain.from_iterable([glob.glob(p) for p in patterns])

    return [os.path.normpath(path) for path in paths]


def _find_build_path(project_path):
    paths = _find_compile_commands_paths(project_path)

    if not paths:
        raise Error('Unable to determine build path. Specify a path manually or '
                    'use one of the standard locations:\n{}'
                    .format('\n'.join(_build_path_patterns('path_to_project',
                                                           'name_of_project_directory'))))
    elif len(paths) > 1:
        raise Error('Multiple {} found:\n{}'
                    .format(compilation_database.COMPILE_COMMANDS_JSON_PATH,
                            '\n'.join(sorted(paths))))

    return os.path.dirname(paths[0])


def _load_config(path):
    try:
        with open(path) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as exception:
        raise Error('Failed to load "{}": {}'.format(path, exception))


class Environment:
    def __init__(self, path_in_project, build_path=None):
        self.project_path = _find_project_path(path_in_project)
        self.build_path = build_path or _find_build_path(self.project_path)
        self.config = _load_config(os.path.join(self.project_path, _DOT_SORK_PATH))

    @property
    def source_paths(self):
        return self.config.get('source_paths', ['.'])

    @source_paths.setter
    def source_paths(self, paths):
        self.config['source_paths'] = paths

    def normalize_path(self, path):
        return os.path.normpath(os.path.relpath(path, start=self.project_path))
