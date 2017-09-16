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

import argparse
import os

from . import commands


_COMMANDS = [
    commands.analyze.AnalyzeCommand(),
    commands.assembler.AssemblerCommand(),
    commands.check.CheckCommand()
]


def _int_argument_greater_than_zero(string: str) -> int:
    value = int(string)
    if value <= 0:
        raise argparse.ArgumentTypeError('invalid value {}, must be > 0'.format(value))
    return value


class Parser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()

        self.add_argument('-bp',
                          '--build-path',
                          help='Path to build directory, automatically detected if possible.',
                          metavar='<path>')

        self.add_argument('-j',
                          '--jobs',
                          default=os.cpu_count() or 1,
                          type=_int_argument_greater_than_zero,
                          help='Run N jobs in parallel. Defaults to number of logical cores '
                               '(%(default)s detected).',
                          metavar='N')

        self.add_argument('-v',
                          '--verbose',
                          action='store_true',
                          help='More verbose output.')

        subparsers = self.add_subparsers(parser_class=argparse.ArgumentParser,
                                         dest='command',
                                         help='-h or --help after <command> for more help',
                                         metavar='<command>')
        # Fix for bug introduced in 3.3.5. See http://bugs.python.org/issue9253#msg186387 .
        subparsers.required = True  # type: ignore

        for cmd in _COMMANDS:
            cmd.add_argparse_subparser(subparsers)


def path_in_project(args: argparse.Namespace) -> str:
    source_paths = args.source_paths if hasattr(args, 'source_paths') else None
    return source_paths[0] if source_paths else os.path.curdir
