# This file is part of Sork.
#
# Copyright (C) 2016-2019 Martin Ejdestig <marejde@gmail.com>
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

import os

from . import config
from . import paths
from .compilation_database import CompilationDatabase


_CONFIG_SCHEMA = config.Schema({
    'source_exclude': config.Value(''),
    'source_paths': config.Value(['.']),

    'checks': config.Value([], types=[config.ListType(str)]),

    'checks.include_guard': config.Value({
        'prefix': config.Value(''),
        'suffix': config.Value('_H'),
        'strip_paths': config.Value(['include', 'src'])
    }),

    'checks.license_header': config.Value({
        'license': config.Value('', types=[config.Type(str), config.ListType(str, min_length=1)]),
        'project': config.Value(''),
        'prefix': config.Value(''),
        'line_prefix': config.Value('// '),
        'suffix': config.Value('')
    })
})


class Project:
    def __init__(self, project_path: str, build_path: str) -> None:
        self.path = project_path
        self.build_path = build_path

        self.config = config.create(os.path.join(self.path, paths.DOT_SORK_PATH), _CONFIG_SCHEMA)

        self.compilation_database = CompilationDatabase(self.path, self.build_path)
