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

import collections
import json
import os


COMPILE_COMMANDS_JSON_PATH = 'compile_commands.json'

CompileCommand = collections.namedtuple('CompileCommand', ['invokation', 'work_dir', 'file'])


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
