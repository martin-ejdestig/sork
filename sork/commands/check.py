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

import re

from .. import checks
from .. import command
from .. import concurrent
from .. import error
from .. import progress_printer
from .. import source


def _check_string_to_names(check_string):
    return [n for n in checks.NAMES if re.match(check_string, n)]


def _check_strings_to_names(check_strings):
    names_set = set()
    if not check_strings or check_strings[0].startswith('-'):
        names_set.update(checks.NAMES)

    for check_string in check_strings:
        disable = check_string.startswith('-')
        names = _check_string_to_names(check_string.lstrip('-'))
        if disable:
            names_set.difference_update(names)
        else:
            names_set.update(names)

    return names_set


def _get_enabled_checks(args, environment):
    check_strings = args.checks.split(',') if args.checks else environment.config['checks']
    names = _check_strings_to_names(check_strings)

    if not names:
        raise error.Error('No checks enabled.')

    return [c(environment) for c in checks.CLASSES if c.NAME in names]


class CheckCommand(command.Command):
    def __init__(self):
        super().__init__('check', arg_help='style check source code')

    def _add_argparse_arguments(self, parser):
        parser.add_argument('-c',
                            '--checks',
                            type=str,
                            help='Comma separated list of checks to perform. Overrides '
                            'configuration in .sork. Prepend - to disable a check. Regular '
                            'expressions may be used. All checks except foo: --checks=-foo . '
                            'Checks starting with clang-: --checks=clang-.* .',
                            metavar='<checks>')

        parser.add_argument('source_paths',
                            nargs='*',
                            help='Check path(s). Directories are recursed. All source code in '
                                 'project, subject to configuration in .sork, is checked if no '
                                 '%(metavar)s is passed or if only %(metavar)s passed is the '
                                 'project\'s root.',
                            metavar='<path>')

    def _run(self, args, environment):
        enabled_checks = _get_enabled_checks(args, environment)
        source_files = source.SourceFinder(environment).find_files(args.source_paths)

        printer = progress_printer.ProgressPrinter()
        printer.start('Checking source', len(source_files))

        def check_source_file(source_file):
            printer.start_with_item(source_file.path)
            outputs = (c.check(source_file) for c in enabled_checks)
            printer.result('\n'.join(o for o in outputs if o))

        try:
            concurrent.for_each(check_source_file, source_files, num_threads=args.jobs)
        except BaseException:
            printer.abort()
            raise
