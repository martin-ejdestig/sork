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
import re
import threading

from typing import Iterator, List, Optional, Pattern

from . import error
from .project import Project


_IN_EXTENSION = '.in'
_C_EXTENSIONS = ['.c']
_CPP_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.C', '.c++']
_HEADER_EXTENSIONS = ['.h', '.hh', '.hp', '.hpp', '.h++', '.hxx']
_EXTENSIONS = _C_EXTENSIONS + _CPP_EXTENSIONS + _HEADER_EXTENSIONS + \
              [e + _IN_EXTENSION for e in _HEADER_EXTENSIONS]


class Error(error.Error):
    pass


class SourceFile:
    def __init__(self, path: str, project: Project) -> None:
        self.path = path
        self.compile_command = project.compilation_database.get_command(path)

        self.project = project

        self._content: str = None
        self._content_lock = threading.Lock()

    @property
    def content(self) -> str:
        with self._content_lock:
            if self._content is None:
                self._content = self._read_content()
            return self._content

    def _read_content(self) -> str:
        with open(os.path.join(self.project.project_path, self.path)) as file:
            return file.read()

    @property
    def is_header(self) -> bool:
        stem, extension = os.path.splitext(self.path)
        if extension == _IN_EXTENSION:
            _, extension = os.path.splitext(stem)
        return extension in _HEADER_EXTENSIONS

    @property
    def stem(self) -> str:
        stem, extension = os.path.splitext(self.path)
        if extension == _IN_EXTENSION:
            stem, _ = os.path.splitext(stem)
        return stem


class SourceFinder:
    def __init__(self, project: Project) -> None:
        self._project = project
        self._normalized_project_path = project.normalize_path(project.project_path)
        self._normalized_build_path = project.normalize_path(project.build_path)
        self._exclude_regex = self._compile_exclude_regex(project)

    @staticmethod
    def _compile_exclude_regex(project: Project) -> Pattern:
        pattern = project.config['source_exclude']
        if not pattern:
            return None
        try:
            return re.compile(pattern)
        except re.error:
            raise Error('Failed to compile \'source_exclude\' regex (\'{}\') in '
                        'configuration.'.format(pattern))

    def find_files(self, source_paths: Optional[List[str]] = None) -> List[SourceFile]:
        if source_paths:
            source_paths = self._project.normalize_paths(source_paths, filter_project_path=True)

        return [SourceFile(path, self._project) for path in self._find_file_paths(source_paths)]

    def find_file(self, path: str) -> SourceFile:
        files = self.find_files([path])

        if len(files) != 1:
            raise Error('Unable to find source file {}.'.format(path))

        return files[0]

    def find_buildable_files(self, source_paths: Optional[List[str]] = None) -> List[SourceFile]:
        return [sf for sf in self.find_files(source_paths) if sf.compile_command]

    def _find_file_paths(self, source_paths: Optional[List[str]] = None) -> List[str]:
        if not source_paths:
            source_paths = self._project.config['source_paths'] or \
                           [self._normalized_project_path]

        self._verify_source_paths(source_paths)

        paths = set()
        dir_paths = []

        for path in source_paths:
            if os.path.isdir(os.path.join(self._project.project_path, path)):
                dir_paths.append(path)
            elif self._should_be_included(path):
                paths.add(path)

        for dir_path in dir_paths:
            paths.update(path for path in self._find_paths_in_dir(dir_path)
                         if self._should_be_included(path))

        return sorted(paths)

    def _verify_source_paths(self, source_paths: List[str]):
        if not source_paths:
            raise Error('No source paths specified.')

        does_not_exist = [path for path in source_paths
                          if not os.path.exists(os.path.join(self._project.project_path, path))]

        if does_not_exist:
            raise Error('The following source paths do not exist:\n{}'.
                        format('\n'.join(does_not_exist)))

    def _should_be_included(self, path: str) -> bool:
        if self._exclude_regex:
            if self._exclude_regex.match(path):
                return False

        if self._normalized_build_path != self._normalized_project_path:
            if os.path.commonpath([self._normalized_build_path, path]):
                return False

        return True

    def _find_paths_in_dir(self, dir_path: str) -> Iterator[str]:
        patterns = [os.path.join(self._project.project_path, dir_path, '**', '*' + extension)
                    for extension in _EXTENSIONS]

        paths = itertools.chain.from_iterable(glob.iglob(pattern, recursive=True)
                                              for pattern in patterns)

        return (self._project.normalize_path(path) for path in paths)
