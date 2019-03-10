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
#
# SPDX-License-Identifier: GPL-3.0-or-later

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


# Declaring these locally in _opcode_count_comment() does not work.
Label = str
Opcode = str
Counters = Dict[Opcode, int]


def _opcode_count_comment(asm: str) -> str:
    def count_opcode(counters: Counters, opcode: Opcode) -> None:
        if opcode in counters:
            counters[opcode] += 1
        else:
            counters[opcode] = 1

    def count_opcodes(asm: str) -> Tuple[Counters, List[Tuple[Label, Counters]]]:
        label_re = r"(?P<label>[a-zA-Z_]+.*):"
        opcode_re = r"\s+(?P<opcode>[a-z]+)\s+"
        regex = re.compile('|'.join([label_re, opcode_re]))

        total: Counters = {}
        current: Counters = total
        per_label: List[Tuple[Label, Counters]] = []

        for line in asm.splitlines(True):
            matches = regex.match(line)
            if not matches:
                continue

            label = matches.group('label')
            if label:
                current = {}
                per_label.append((label, current))

            opcode = matches.group('opcode')
            if opcode:
                count_opcode(total, opcode)
                count_opcode(current, opcode)

        return total, per_label

    total, per_label = count_opcodes(asm)
    total_label = 'Total opcode count'
    labels_and_counters = [(total_label, total)] if len(per_label) > 1 else []
    labels_and_counters += per_label

    comment = ''

    for label, counters in labels_and_counters:
        if counters:
            comment += '# ' + label + ':\n'
            for opcode, count in sorted(counters.items()):
                comment += '#\t' + opcode + ': ' + str(count) + '\n'
            comment += '#\n'

    return comment


def add_argparse_subparser(subparsers: argparse.Action, source_paths_arg_name: str) -> None:
    # TODO: Better fix? Have to silence mypy since Action does not have add_parser() and
    #       argparse._SubParserAction is not public.
    parser = subparsers.add_parser('asm',  # type: ignore
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


def run(args: argparse.Namespace, project: Project) -> None:
    source_file = source.find_file(project, args.source_paths[0])
    asm = _assembler_for_source_file(source_file, args.verbose_asm)

    if args.count:
        asm = _opcode_count_comment(asm) + asm

    print(asm)
