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

import argparse
import os

from . import analyze
from . import assembler
from . import check
from . import environment


def _create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-bp',
                        '--build-path',
                        help='path to build directory, automatically detected if possible',
                        metavar='<path>')
    subparsers = parser.add_subparsers(dest='command',
                                       help='-h or --help after <command> for more help',
                                       metavar='<command>')
    # Fix for bug introduced in 3.3.5. See http://bugs.python.org/issue9253#msg186387 .
    subparsers.required = True

    parser_analyze = subparsers.add_parser('analyze',
                                           help='run static analyzer')
    parser_analyze.add_argument('source_paths',
                                nargs='*',
                                help='analyze path(s) (directories are recursed)',
                                metavar='<path>')

    parser_assembler = subparsers.add_parser('asm',
                                             aliases=['assembler'],
                                             help='output assembler for compilation unit')
    parser_assembler.add_argument('source_paths',
                                  nargs=1,
                                  help='source file to output assembler for',
                                  metavar='<file>')

    parser_check = subparsers.add_parser('check',
                                         help='style check source code')
    parser_check.add_argument('-f',
                              '--fix',
                              action='store_true',
                              help='fix violations (NOTE: modifies source files) (TODO)')
    parser_check.add_argument('source_paths',
                              nargs='*',
                              help='only check path(s) (directories are recursed)',
                              metavar='<path>')

    return parser


def _create_environment(arg_parser, args):
    source_paths = args.source_paths if hasattr(args, 'source_paths') else None

    if source_paths:
        path_in_project = source_paths[0]
        if os.path.isfile(path_in_project):
            path_in_project = os.path.dirname(path_in_project)
    else:
        path_in_project = os.path.curdir

    try:
        env = environment.Environment(path_in_project, build_path=args.build_path)
    except environment.Error as error:
        print(error)
        arg_parser.print_help()
        arg_parser.exit(1)

    if source_paths:
        normalized_paths = (env.normalize_path(path) for path in source_paths)
        filtered_paths = [path for path in normalized_paths
                          if path != environment.NORMALIZED_PROJECT_PATH]
        if filtered_paths:  # Empty if only project path (should not override what is in config).
            env.config['source_paths'] = filtered_paths

    return env


def _run_command(args, env):
    try:
        if args.command == 'analyze':
            analyze.analyze(env)
        elif args.command in ['asm', 'assembler']:
            assembler.output_for_source_file(env, args.source_paths[0])
        elif args.command == 'check':
            check.check(env)
        else:
            assert False
    except KeyboardInterrupt:
        pass


def main():
    arg_parser = _create_arg_parser()
    args = arg_parser.parse_args()
    env = _create_environment(arg_parser, args)

    _run_command(args, env)
