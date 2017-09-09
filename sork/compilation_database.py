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

import json
import os

from typing import Dict, List, Optional

from . import error
from . import paths


class Command:
    def __init__(self, invokation: str, work_dir: str, file: str) -> None:
        self.invokation = invokation
        self.work_dir = work_dir
        self.file = file


class CompilationDatabase:
    def __init__(self, project_path: str, build_path: str) -> None:
        self.path = os.path.join(build_path, paths.COMPILE_COMMANDS_JSON_PATH)

        self._commands = self._load(project_path)

    def _load(self, project_path: str) -> Dict[str, Command]:
        try:
            with open(self.path) as file:
                entries = json.load(file)
        except Exception as exception:
            raise error.Error('{}: {}'.format(self.path, exception))

        return self._json_entries_to_commands(entries, project_path)

    @staticmethod
    def _json_entries_to_commands(entries: List[Dict[str, str]],
                                  project_path: str) -> Dict[str, Command]:
        commands = {}

        for entry in entries:
            path = os.path.join(entry['directory'], entry['file'])
            relpath = os.path.relpath(path, start=project_path)
            normpath = os.path.normpath(relpath)
            commands[normpath] = Command(entry['command'], entry['directory'], entry['file'])

        return commands

    def get_command(self, path: str) -> Optional[Command]:
        return self._commands.get(path)
