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

import argparse

from .. import checks
from .. import concurrent
from ..project import Project
from ..progress_printer import ProgressPrinter
from ..source import SourceFile, SourceFinder


def add_argparse_subparser(subparsers, source_paths_arg_name: str):
    parser = subparsers.add_parser('check', help='style check source code')

    parser.set_defaults(run_command=run)

    parser.add_argument('-c',
                        '--checks',
                        type=str,
                        help='Comma separated list of checks to perform. Overrides '
                             'configuration in .sork. Prepend - to disable a check. Regular '
                             'expressions may be used. All checks except foo: --checks=-foo . '
                             'Checks starting with clang-: --checks=clang-.* .',
                        metavar='<checks>')

    parser.add_argument(source_paths_arg_name,
                        nargs='*',
                        help='Check path(s). Directories are recursed. All source code in '
                             'project, subject to configuration in .sork, is checked if no '
                             '%(metavar)s is passed or if only %(metavar)s passed is the '
                             'project\'s root.',
                        metavar='<path>')


def run(args: argparse.Namespace, project: Project):
    check_strings = args.checks.split(',') if args.checks else project.config['checks']
    enabled_checks = checks.create.from_strings(project, check_strings)

    source_files = SourceFinder(project).find_files(args.source_paths)

    printer = ProgressPrinter(verbose=args.verbose)
    printer.start('Checking source', len(source_files))

    def check_source_file(source_file: SourceFile):
        printer.start_with_item(source_file.path)
        outputs = (c.check(source_file) for c in enabled_checks)
        printer.done_with_item('\n'.join(o for o in outputs if o))

    try:
        concurrent.for_each(check_source_file, source_files, num_threads=args.jobs)
    except BaseException:
        printer.abort()
        raise
