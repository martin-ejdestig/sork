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

import re
import subprocess

from .. import command
from .. import concurrent
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
        super().__init__()

    def add_arg_subparser(self, subparsers):
        parser = self._create_arg_subparser(subparsers,
                                            'analyze',
                                            arg_help='run static analyzer')

        parser.add_argument('source_paths',
                            nargs='*',
                            help='analyze path(s) (directories are recursed)',
                            metavar='<path>')

    def run(self, args, environment):
        source_files = [sf for sf in source.find_source_files(environment)
                        if sf.compile_command]
        concurrent.for_each_with_progress_printer('Analyzing source',
                                                  _analyze_source_file,
                                                  source_files)
