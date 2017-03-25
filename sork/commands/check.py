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


def _check_string_to_check_names(check_string):
    return [n for n in checks.NAMES if re.match(check_string, n)]


def _check_strings_to_check_names(check_strings):
    check_names = set()
    if not check_strings or check_strings[0].startswith('-'):
        check_names.update(checks.NAMES)

    for check_string in check_strings:
        disable = check_string.startswith('-')
        names = _check_string_to_check_names(check_string.lstrip('-'))
        if disable:
            check_names.difference_update(names)
        else:
            check_names.update(names)

    return check_names


def _get_enabled_checks(args, environment):
    check_strings = args.checks.split(',') if args.checks else environment.config['checks']
    names = _check_strings_to_check_names(check_strings)
    return [c(environment) for c in checks.CLASSES if c.name in names]


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
        try:
            _run_checks(args, environment)
        except (check.Error, source.Error) as error:
            raise command.Error(error)
