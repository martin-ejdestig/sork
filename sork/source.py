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

import glob
import itertools
import os
import re
import threading

from . import compilation_database


_IN_EXTENSION = '.in'
_C_EXTENSIONS = ['.c']
_CPP_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.C', '.c++']
_HEADER_EXTENSIONS = ['.h', '.hh' '.hp', '.hpp', '.h++', '.hxx']
_EXTENSIONS = _C_EXTENSIONS + _CPP_EXTENSIONS + _HEADER_EXTENSIONS + \
              [e + _IN_EXTENSION for e in _HEADER_EXTENSIONS]


class Error(Exception):
    pass


class SourceFile:
    def __init__(self, path, compile_command, environment):
        self.path = path
        self.compile_command = compile_command

        self._environment = environment

        self._content = None
        self._content_lock = threading.Lock()

    @property
    def content(self):
        with self._content_lock:
            if not self._content:
                self._content = self._read_content()
            return self._content

    def _read_content(self):
        with open(os.path.join(self._environment.project_path, self.path)) as file:
            return file.read()

    @property
    def is_header(self):
        stem, extension = os.path.splitext(self.path)
        if extension == _IN_EXTENSION:
            _, extension = os.path.splitext(stem)
        return extension in _HEADER_EXTENSIONS

    @property
    def stem(self):
        stem, extension = os.path.splitext(self.path)
        if extension == _IN_EXTENSION:
            stem, _ = os.path.splitext(stem)
        return stem


def _get_exclude_regex(environment):
    pattern = environment.config['source_exclude']
    if not pattern:
        return None
    try:
        return re.compile(pattern)
    except re.error:
        return None


def _verify_source_paths(environment, source_paths):
    if not source_paths:
        raise Error('No source paths specified.')

    does_not_exist = [path for path in source_paths
                      if not os.path.exists(os.path.join(environment.project_path, path))]

    if does_not_exist:
        raise Error('The following source paths do not exist:\n{}'.
                    format('\n'.join(does_not_exist)))


def _find_source_file_paths(environment, source_paths=None):
    project_path = environment.normalize_path(environment.project_path)

    if not source_paths:
        source_paths = environment.config['source_paths'] or project_path
    _verify_source_paths(environment, source_paths)

    paths = set()
    dir_paths = []

    exclude_regex = _get_exclude_regex(environment)
    build_path = environment.normalize_path(environment.build_path)
    if build_path == project_path:
        build_path = None

    def should_be_included(path):
        if exclude_regex and exclude_regex.match(path):
            return False
        if build_path and os.path.commonpath([build_path, path]):
            return False
        return True

    for path in source_paths:
        if os.path.isdir(os.path.join(environment.project_path, path)):
            dir_paths.append(path)
        elif should_be_included(path):
            paths.add(path)

    for dir_path, extension in itertools.product(dir_paths, _EXTENSIONS):
        pattern = os.path.join(environment.project_path, dir_path, '**', '*' + extension)
        found_paths = (environment.normalize_path(path)
                       for path in glob.glob(pattern, recursive=True))
        paths.update(path for path in found_paths if should_be_included(path))

    return sorted(paths)


def find_source_files(environment, paths=None):
    normpaths = environment.normalize_paths(paths, filter_project_path=True) if paths else None
    compile_commands = compilation_database.load_from_file(environment)

    return [SourceFile(path, compile_commands.get(path), environment)
            for path in _find_source_file_paths(environment, normpaths)]


def get_source_file(environment, path):
    files = find_source_files(environment, [path])

    if len(files) != 1:
        raise Error('Unable to find source file {}.'.format(path))

    return files[0]
