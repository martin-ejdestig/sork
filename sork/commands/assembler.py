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
import re
import subprocess

from typing import Dict, List, Tuple

from .. import error
from .. import source
from ..project import Project


class Error(error.Error):
    pass


def _assembler_for_source_file(source_file: source.SourceFile, verbose: bool = False) -> str:
    if not source_file.compile_command:
        raise Error('Do not know how to compile "{}".'.format(source_file.path))

    output_asm_args = '-S'
    if verbose:
        output_asm_args += ' -fverbose-asm'

    command_args = source_file.compile_command.invocation
    command_args = re.sub(r" -c ", ' ' + output_asm_args + ' ', command_args)
    command_args = re.sub(r" -o '?.*\.o'? ", ' -o- ', command_args)
    command_args = re.sub(r" '?-M(?:[MGPD]|MD)?'?(?= )", '', command_args)
    command_args = re.sub(r" '?-M[FTQ]'? '?.*?\.[do]'?(?= )", '', command_args)

    with subprocess.Popen(command_args,
                          stdout=subprocess.PIPE,
                          cwd=source_file.compile_command.work_dir,
                          shell=True,
                          universal_newlines=True) as process:
        stdout, _ = process.communicate()
        if process.returncode != 0:
            raise Error('Failed to run compiler command for outputting assembler.')

    return stdout


class OpcodeCounter:
    def __init__(self) -> None:
        self._total: Dict[str, int] = {}
        self._current: Dict[str, int] = self._total
        self._per_label: List[Tuple[str, Dict[str, int]]] = []

    def count_in_string(self, asm: str):
        label_re = r"(?P<label>[a-zA-Z_]+.*):"
        opcode_re = r"\s+(?P<opcode>[a-z]+)\s+"
        regex = re.compile('|'.join([label_re, opcode_re]))

        for line in asm.splitlines(True):
            matches = regex.match(line)
            if not matches:
                continue

            label = matches.group('label')
            if label:
                self._current = {}
                self._per_label.append((label, self._current))

            opcode = matches.group('opcode')
            if opcode:
                self._count_opcode(self._total, opcode)
                self._count_opcode(self._current, opcode)

    @staticmethod
    def _count_opcode(counters: Dict[str, int], opcode: str):
        if opcode in counters:
            counters[opcode] += 1
        else:
            counters[opcode] = 1

    def get_comment(self) -> str:
        total_label = 'Total opcode count'
        labels_and_counters = [(total_label, self._total)] if len(self._per_label) > 1 else []
        labels_and_counters += self._per_label

        comment = ''

        for label, counters in labels_and_counters:
            if counters:
                comment += '# ' + label + ':\n'
                for opcode, count in sorted(counters.items()):
                    comment += '#\t' + opcode + ': ' + str(count) + '\n'
                comment += '#\n'

        return comment


def add_argparse_subparser(subparsers, source_paths_arg_name: str):
    parser = subparsers.add_parser('asm',
                                   aliases=['assembler'],
                                   help='output assembler for compilation unit')

    parser.set_defaults(run_command=run)

    parser.add_argument('-c',
                        '--count',
                        action='store_true',
                        help='Count occurance of different opcodes per global label and in '
                             'total if there is more than one global label. Result is printed '
                             'as a comment before the generated assembly.')

    parser.add_argument('-va',
                        '--verbose-asm',
                        action='store_true',
                        help='Tell compiler to output verbose assembler.')

    parser.add_argument(source_paths_arg_name,
                        nargs=1,
                        help='Source file to output assembler for.',
                        metavar='<file>')


def run(args: argparse.Namespace, project: Project):
    source_file = source.find_file(project, args.source_paths[0])
    asm = _assembler_for_source_file(source_file, args.verbose_asm)

    if args.count:
        counter = OpcodeCounter()
        counter.count_in_string(asm)
        asm = counter.get_comment() + asm

    print(asm)
