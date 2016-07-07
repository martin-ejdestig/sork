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

import re
import subprocess

from .. import command
from .. import source


def _output_for_source_file(args, environment):
    path = args.source_paths[0]
    source_file = source.get_source_file(environment, path)

    if not source_file.compile_command:
        raise command.Error('Do not know how to compile "{}".'.format(path))

    args = source_file.compile_command.invokation
    args = re.sub(r" -c ", ' -S ', args)
    args = re.sub(r" -o '?.*\.o'? ", ' -o- ', args)
    args = re.sub(r" '?-M(?:[MGPD]|MD)?'?(?= )", '', args)
    args = re.sub(r" '?-M[FTQ]'? '?.*?\.[do]'?(?= )", '', args)

    with subprocess.Popen(args,
                          cwd=source_file.compile_command.work_dir,
                          shell=True) as process:
        if process.wait() != 0:
            raise command.Error('Failed to run compiler command for outputting assembler.')


class AssemblerCommand(command.Command):
    def __init__(self):
        super().__init__()

    def add_arg_subparser(self, subparsers):
        parser = self._create_arg_subparser(subparsers,
                                            'asm',
                                            aliases=['assembler'],
                                            arg_help='output assembler for compilation unit')

        parser.add_argument('source_paths',
                            nargs=1,
                            help='source file to output assembler for',
                            metavar='<file>')

    def run(self, args, environment):
        _output_for_source_file(args, environment)
