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

from .. import checks
from .. import command
from .. import concurrent
from .. import source


_CHECKS = [
    checks.clang_format.ClangFormatCheck(),
    checks.clang_tidy.ClangTidyCheck(),
    checks.include_guard.IncludeGuardCheck()
]


def _check_source_file(source_file):
    outputs = (c.check(source_file) for c in _CHECKS)
    return '\n'.join(o for o in outputs if o)


class CheckCommand(command.Command):
    def __init__(self):
        super().__init__('check', arg_help='style check source code')

    def _add_argparse_arguments(self, parser):
        parser.add_argument('-f',
                            '--fix',
                            action='store_true',
                            help='fix violations (NOTE: modifies source files) (TODO)')

        parser.add_argument('source_paths',
                            nargs='*',
                            help='only check path(s) (directories are recursed)',
                            metavar='<path>')

    def _run(self, args, environment):
        concurrent.for_each_with_progress_printer('Checking source',
                                                  _check_source_file,
                                                  source.find_source_files(environment,
                                                                           args.source_paths),
                                                  num_threads=args.jobs)
