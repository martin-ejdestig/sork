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
import sys

from . import commands
from . import error
from . import paths
from .environment import Environment


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


def _create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('-bp',
                        '--build-path',
                        help='Path to build directory, automatically detected if possible.',
                        metavar='<path>')

    parser.add_argument('-j',
                        '--jobs',
                        default=os.cpu_count() or 1,
                        type=_int_argument_greater_than_zero,
                        help='Run N jobs in parallel. Defaults to number of logical cores '
                             '(%(default)s detected).',
                        metavar='N')

    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='More verbose output.')

    subparsers = parser.add_subparsers(dest='command',
                                       help='-h or --help after <command> for more help',
                                       metavar='<command>')
    # Fix for bug introduced in 3.3.5. See http://bugs.python.org/issue9253#msg186387 .
    subparsers.required = True  # type: ignore

    for cmd in _COMMANDS:
        cmd.add_argparse_subparser(subparsers)

    return parser


def _path_in_project(args: argparse.Namespace) -> str:
    source_paths = args.source_paths if hasattr(args, 'source_paths') else None
    return source_paths[0] if source_paths else os.path.curdir


def _create_environment(args: argparse.Namespace) -> Environment:
    project_path = paths.find_project_path(_path_in_project(args))
    build_path = args.build_path or paths.find_build_path(project_path)
    return Environment(project_path, build_path)


def main():
    arg_parser = _create_arg_parser()
    args = arg_parser.parse_args()

    try:
        env = _create_environment(args)
        args.run_command(args, env)
    except KeyboardInterrupt:
        pass
    except error.Error as exception:
        print(exception)
        sys.exit(1)
