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
import os
import threading

from . import compilation_database


_IN_EXTENSION = '.in'
_C_EXTENSIONS = ['.c']
_CPP_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.C', '.c++']
_HEADER_EXTENSIONS = ['.h', '.hh' '.hp', '.hpp', '.h++', '.hxx']
_EXTENSIONS = _C_EXTENSIONS + _CPP_EXTENSIONS + _HEADER_EXTENSIONS + \
              [e + _IN_EXTENSION for e in _HEADER_EXTENSIONS]


class SourceFile:
    def __init__(self, path, compile_command, environment):
        self.path = path
        self.compile_command = compile_command
        self.environment = environment

        self._content = None
        self._content_lock = threading.Lock()

    @property
    def content(self):
        with self._content_lock:
            if not self._content:
                self._content = self._read_content()
            return self._content

    def _read_content(self):
        with open(os.path.join(self.environment.project_path, self.path)) as file:
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


def _find_source_file_paths(environment):
    paths = set()
    dir_paths = []

    for path in environment.source_paths:
        if os.path.isdir(os.path.join(environment.project_path, path)):
            dir_paths.append(path)
        else:
            paths.add(path)

    for dir_path, extension in itertools.product(dir_paths, _EXTENSIONS):
        pattern = os.path.join(environment.project_path, dir_path, '**', '*' + extension)
        paths.update(environment.normalize_path(path)
                     for path in glob.glob(pattern, recursive=True))

    return sorted(paths)


def find_source_files(environment):
    paths = _find_source_file_paths(environment)
    compile_commands = compilation_database.load_from_file(environment)

    return [SourceFile(path, compile_commands.get(path), environment) for path in paths]


def get_source_file(environment, path):
    normpath = environment.normalize_path(path)
    compile_commands = compilation_database.load_from_file(environment)

    return SourceFile(normpath, compile_commands.get(normpath), environment)
