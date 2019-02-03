# This file is part of Sork.
#
# Copyright (C) 2016-2019 Martin Ejdestig <marejde@gmail.com>
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

from .. import concurrent
from .. import source
from ..project import Project
from ..progress_printer import ProgressPrinter


def _analyze_source_file(source_file: source.SourceFile) -> str:
    assert source_file.compile_command

    args = source_file.compile_command.invocation
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


def add_argparse_subparser(subparsers: argparse.Action, source_paths_arg_name: str) -> None:
    # TODO: Better fix? Have to silence mypy since Action does not have add_parser() and
    #       argparse._SubParserAction is not public.
    parser = subparsers.add_parser('analyze', help='run static analyzer')  # type: ignore

    parser.set_defaults(run_command=run)

    parser.add_argument(source_paths_arg_name,
                        nargs='*',
                        help='Analyze path(s). Directories are recursed. All source code in '
                             'project, subject to configuration in .sork, is analyzed if no '
                             '%(metavar)s is passed or if only %(metavar)s passed is the '
                             'project\'s root.',
                        metavar='<path>')


def run(args: argparse.Namespace, project: Project) -> None:
    source_files = source.find_buildable_files(project, args.source_paths)

    printer = ProgressPrinter(verbose=args.verbose)
    printer.start('Analyzing source', len(source_files))

    def analyze(source_file: source.SourceFile) -> None:
        printer.start_with_item(source_file.path)
        output = _analyze_source_file(source_file)
        printer.done_with_item(output)

    try:
        concurrent.for_each(analyze, source_files, num_threads=args.jobs)
    except BaseException:
        printer.abort()
        raise
