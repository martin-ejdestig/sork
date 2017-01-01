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

from .. import check
from .. import checks
from .. import command
from .. import concurrent
from .. import source


def _get_enabled_checks(args, environment):
    checks_string = args.checks or environment.config['checks']
    enabled_names = set()
    if not checks_string or checks_string.startswith('-'):
        enabled_names.update(checks.NAMES)

    for check_string in checks_string.split(','):
        disable = check_string.startswith('-')
        pattern = check_string.lstrip('-')
        names = [n for n in checks.NAMES if re.match(pattern, n)]
        if disable:
            enabled_names.difference_update(names)
        else:
            enabled_names.update(names)

    return [c(environment) for c in checks.CLASSES if c.name in enabled_names]


def _run_checks(args, environment):
    enabled_checks = _get_enabled_checks(args, environment)

    if not enabled_checks:
        raise command.Error('No checks enabled.')

    def check_source_file(source_file):
        outputs = (c.check(source_file) for c in enabled_checks)
        return '\n'.join(o for o in outputs if o)

    concurrent.for_each_with_progress_printer('Checking source',
                                              check_source_file,
                                              source.find_source_files(environment,
                                                                       args.source_paths),
                                              num_threads=args.jobs)


class CheckCommand(command.Command):
    def __init__(self):
        super().__init__('check', arg_help='style check source code')

    def _add_argparse_arguments(self, parser):
        parser.add_argument('-c',
                            '--checks',
                            type=str,
                            help='Comma separated list of checks to perform. Defaults to all '
                            'checks. Prepend - to disable a check. Regular expressions may be '
                            'used. All checks except foo: --checks=-foo . Checks starting with '
                            'clang- not containing bar: --checks=clang-.*,-.*bar.* .',
                            metavar='<checks>')

        parser.add_argument('-f',
                            '--fix',
                            action='store_true',
                            help='Fix violations (NOTE: modifies source files) (TODO).')

        parser.add_argument('source_paths',
                            nargs='*',
                            help='Only check path(s) (directories are recursed).',
                            metavar='<path>')

    def _run(self, args, environment):
        try:
            _run_checks(args, environment)
        except (check.Error, source.Error) as error:
            raise command.Error(error)
