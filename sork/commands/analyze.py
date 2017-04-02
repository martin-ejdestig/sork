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
import subprocess

from .. import command
from .. import concurrent
from .. import progress_printer
from .. import source


def _analyze_source_file(source_file):
    args = source_file.compile_command.invokation
    args = re.sub(r"^.*?\+\+", 'clang++ --analyze -Xanalyzer -analyzer-output=text', args)
    args = re.sub(r" -c", '', args)
    args = re.sub(r" -o '?.*\.o'?", '', args)
    args = re.sub(r" '?-pipe'?", '', args)
    args = re.sub(r" '?-W[a-z0-9-=]+'?", '', args)
    args = re.sub(r" '?-M(?:[MGPD]|MD)?'?(?= )", '', args)
    args = re.sub(r" '?-M[FTQ]'? '?.*?\.[do]'?(?= )", '', args)

    with subprocess.Popen(args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          shell=True,
                          cwd=source_file.compile_command.work_dir,
                          universal_newlines=True) as process:
        return process.communicate()[0]


class AnalyzeCommand(command.Command):
    def __init__(self):
        super().__init__('analyze', arg_help='run static analyzer')

    def _add_argparse_arguments(self, parser):
        parser.add_argument('source_paths',
                            nargs='*',
                            help='Analyze path(s). Directories are recursed. All source code in '
                                 'project, subject to configuration in .sork, is analyzed if no '
                                 '%(metavar)s is passed or if only %(metavar)s passed is the '
                                 'project\'s root.',
                            metavar='<path>')

    def _run(self, args, environment):
        source_files = source.SourceFinder(environment).find_buildable_files(args.source_paths)

        printer = progress_printer.ProgressPrinter()
        printer.start('Analyzing source', len(source_files))

        def analyze(source_file):
            printer.result(_analyze_source_file(source_file))

        try:
            concurrent.for_each(analyze, source_files, num_threads=args.jobs)
        except BaseException:
            printer.abort()
            raise
