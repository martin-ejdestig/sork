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

import json
import os

from typing import Dict, List

from . import error
from . import paths


class Error(error.Error):
    pass


class Command:
    def __init__(self, invocation: str, work_dir: str, file: str) -> None:
        self.invocation = invocation
        self.work_dir = work_dir
        self.file = file


class CompilationDatabase:
    def __init__(self, project_path: str, build_path: str) -> None:
        def load_json(path: str) -> List[Dict[str, str]]:
            try:
                with open(path) as file:
                    entries = json.load(file)
            except Exception as exception:
                raise Error('{}: {}'.format(path, exception))

            if not isinstance(entries, list):
                raise Error('{}: expected top element to be a list.'.format(path))

            for entry in entries:
                if not isinstance(entry, dict):
                    raise Error('{}: all entries in top list must be objects.'.format(path))

                if not all(key in entry.keys() for key in ['command', 'directory', 'file']):
                    raise Error('{}: all entries must contain command, directory and '
                                'file keys.'.format(path))

                if not all(isinstance(value, str) for value in entry.values()):
                    raise Error('{}: all values in entries must be strings.'.format(path))

            return entries

        def json_entries_to_commands(entries: List[Dict[str, str]],
                                     project_path: str) -> Dict[str, Command]:
            commands = {}

            for entry in entries:
                path = os.path.join(entry['directory'], entry['file'])
                relpath = os.path.relpath(path, start=project_path)
                normpath = os.path.normpath(relpath)
                commands[normpath] = Command(entry['command'], entry['directory'], entry['file'])

            return commands

        path = os.path.join(build_path, paths.COMPILE_COMMANDS_JSON_PATH)
        entries = load_json(path)
        self.commands = json_entries_to_commands(entries, project_path)
