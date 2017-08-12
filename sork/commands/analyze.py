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
import re
import subprocess

from . import command

from .. import concurrent
from ..environment import Environment
from ..progress_printer import ProgressPrinter
from ..source import SourceFile, SourceFinder


def _analyze_source_file(source_file: SourceFile) -> str:
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
                          env=source_file.environment.command_env_vars(),
                          universal_newlines=True) as process:
        return process.communicate()[0]


class AnalyzeCommand(command.Command):
    def __init__(self) -> None:
        super().__init__('analyze', arg_help='run static analyzer')

    def _add_argparse_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('source_paths',
                            nargs='*',
                            help='Analyze path(s). Directories are recursed. All source code in '
                                 'project, subject to configuration in .sork, is analyzed if no '
                                 '%(metavar)s is passed or if only %(metavar)s passed is the '
                                 'project\'s root.',
                            metavar='<path>')

    def _run(self, args: argparse.Namespace, environment: Environment):
        source_files = SourceFinder(environment).find_buildable_files(args.source_paths)

        printer = ProgressPrinter(verbose=args.verbose)
        printer.start('Analyzing source', len(source_files))

        def analyze(source_file: SourceFile):
            printer.start_with_item(source_file.path)
            output = _analyze_source_file(source_file)
            printer.done_with_item(output)

        try:
            concurrent.for_each(analyze, source_files, num_threads=args.jobs)
        except BaseException:
            printer.abort()
            raise
