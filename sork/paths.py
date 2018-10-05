# This file is part of Sork.
#
# Copyright (C) 2016-2018 Martin Ejdestig <marejde@gmail.com>
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
import os

from typing import List

from . import error


DOT_SORK_PATH = '.sork'

_DOT_PATHS_IN_PROJECT_ROOT = ['.git', DOT_SORK_PATH]

COMPILE_COMMANDS_JSON_PATH = 'compile_commands.json'

NORMALIZED_PROJECT_PATH = os.path.curdir


class Error(error.Error):
    pass


def _is_project_path(path: str) -> bool:
    return any(os.path.exists(os.path.join(path, dp))
               for dp in _DOT_PATHS_IN_PROJECT_ROOT)


def find_project_path(path_in_project: str) -> str:
    path = os.path.dirname(path_in_project) if os.path.isfile(path_in_project) else path_in_project

    while not _is_project_path(path):
        parent_path = os.path.relpath(os.path.join(path, os.path.pardir))

        if path == parent_path:
            raise Error('Unable to determine project root path. '
                        'Currently looking for: {}'
                        .format(', '.join(_DOT_PATHS_IN_PROJECT_ROOT)))

        path = parent_path

    return path


def _build_path_patterns(project_path: str, basename: str) -> List[str]:
    pattern_dir_components = [
        ['*'],
        [os.path.pardir, basename + '*'],
        [os.path.pardir, 'build*', basename + '*'],
        [os.path.pardir, 'build-' + basename + '*']
    ]
    return [os.path.join(project_path, *cs) for cs in pattern_dir_components]


def _find_potential_build_paths(project_path: str) -> List[str]:
    basename = os.path.basename(os.path.abspath(project_path))

    patterns = [os.path.join(pattern, COMPILE_COMMANDS_JSON_PATH)
                for pattern in _build_path_patterns(project_path, basename)]

    paths = itertools.chain.from_iterable([glob.glob(p) for p in patterns])

    return [os.path.dirname(os.path.normpath(path)) for path in paths]


def find_build_path(project_path: str) -> str:
    paths = _find_potential_build_paths(project_path)

    if not paths:
        standard_locations = _build_path_patterns('path_to_project',
                                                  'name_of_project_directory')
        raise Error('Unable to determine build path. Specify a path manually or '
                    'use one of the standard locations:\n{}'
                    .format('\n'.join(standard_locations)))

    if len(paths) > 1:
        raise Error('Multiple build paths found, specify a path manually:\n{}'
                    .format('\n'.join(sorted(paths))))

    return paths[0]


def normalize_path(project_path: str, unnormalized_path: str) -> str:
    return os.path.normpath(os.path.relpath(unnormalized_path, start=project_path))


def normalize_paths(project_path: str,
                    unnormalized_paths: List[str],
                    filter_project_path: bool = False) -> List[str]:
    normalized_paths = [normalize_path(project_path, path) for path in unnormalized_paths]
    if filter_project_path:
        normalized_paths = [path for path in normalized_paths
                            if path != NORMALIZED_PROJECT_PATH]
    return normalized_paths
