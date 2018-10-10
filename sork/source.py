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

from typing import Iterator, List, Optional

from . import error
from . import paths
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
        self.compile_command = project.compilation_database.commands.get(path)

        self.project = project

        self._content: Optional[str] = None
        self._content_lock = threading.Lock()

    @property
    def content(self) -> str:
        with self._content_lock:
            if self._content is None:
                self._content = self._read_content()
            return self._content

    def _read_content(self) -> str:
        with open(os.path.join(self.project.path, self.path)) as file:
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


def find_files(project: Project, source_paths: Optional[List[str]] = None) -> List[SourceFile]:
    normalized_build_path = paths.normalize_path(project.path, project.build_path)

    if source_paths:
        source_paths = paths.normalize_paths(project.path, source_paths, filter_project_path=True)
    if not source_paths:
        source_paths = project.config['source_paths'] or [paths.NORMALIZED_PROJECT_PATH]

    try:
        exclude_pattern = project.config['source_exclude']
        exclude_regex = re.compile(exclude_pattern) if exclude_pattern else None
    except re.error:
        raise Error('Failed to compile \'source_exclude\' regex (\'{}\') in '
                    'configuration.'.format(exclude_pattern))

    def verify_paths_exist(source_paths: List[str]):
        if not source_paths:
            raise Error('No source paths specified.')

        does_not_exist = [path for path in source_paths
                          if not os.path.exists(os.path.join(project.path, path))]

        if does_not_exist:
            raise Error('The following source paths do not exist:\n{}'.
                        format('\n'.join(does_not_exist)))

    def should_be_included(path: str) -> bool:
        if exclude_regex:
            if exclude_regex.match(path):
                return False

        if normalized_build_path != paths.NORMALIZED_PROJECT_PATH:
            if os.path.commonpath([normalized_build_path, path]):
                return False

        return True

    def find_paths_in_dir(dir_path: str) -> Iterator[str]:
        patterns = [os.path.join(project.path, dir_path, '**', '*' + extension)
                    for extension in _EXTENSIONS]

        found_paths = itertools.chain.from_iterable(glob.iglob(pattern, recursive=True)
                                                    for pattern in patterns)

        return (paths.normalize_path(project.path, path) for path in found_paths)

    def find_file_paths(search_paths: List[str]) -> List[str]:
        file_paths = set()
        dir_paths = []

        for path in search_paths:
            if os.path.isdir(os.path.join(project.path, path)):
                dir_paths.append(path)
            elif should_be_included(path):
                file_paths.add(path)

        for dir_path in dir_paths:
            file_paths.update(path for path in find_paths_in_dir(dir_path)
                              if should_be_included(path))

        return sorted(file_paths)

    verify_paths_exist(source_paths)

    return [SourceFile(path, project) for path in find_file_paths(source_paths)]


def find_file(project: Project, path: str) -> SourceFile:
    files = find_files(project, [path])

    if len(files) != 1:
        raise Error('Unable to find source file {}.'.format(path))

    return files[0]


def find_buildable_files(project: Project,
                         source_paths: Optional[List[str]] = None) -> List[SourceFile]:
    return [sf for sf in find_files(project, source_paths) if sf.compile_command]
