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
from .. import error
from .. import source


def _assembler_for_source_file(source_file, verbose=False):
    if not source_file.compile_command:
        raise error.Error('Do not know how to compile "{}".'.format(source_file.path))

    output_asm_args = '-S'
    if verbose:
        output_asm_args += ' -fverbose-asm'

    command_args = source_file.compile_command.invokation
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
            raise error.Error('Failed to run compiler command for outputting assembler.')

    return stdout


class OpcodeCounter:
    def __init__(self):
        self._total = {}
        self._current = self._total
        self._per_label = []

    def count_in_string(self, asm):
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
    def _count_opcode(counters, opcode):
        if opcode in counters:
            counters[opcode] += 1
        else:
            counters[opcode] = 1

    def get_comment(self):
        total_label = 'Total opcode count'
        labels_and_counters = [(total_label, self._total)] if len(self._per_label) > 1 else []
        labels_and_counters += self._per_label

        comment = ''

        for label, counters in labels_and_counters:
            comment += '# ' + label + ':\n'
            for opcode, count in sorted(counters.items()):
                comment += '#\t' + opcode + ': ' + str(count) + '\n'
            comment += '#\n'

        return comment


class AssemblerCommand(command.Command):
    def __init__(self):
        super().__init__('asm',
                         aliases=['assembler'],
                         arg_help='output assembler for compilation unit')

    def _add_argparse_arguments(self, parser):
        parser.add_argument('-c',
                            '--count',
                            action='store_true',
                            help='Count occurance of different opcodes per global label and in '
                                 'total if there is more than one global label. Result is printed '
                                 'as a comment before the generated assembly.')

        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='Tell compiler to output verbose assembler.')

        parser.add_argument('source_paths',
                            nargs=1,
                            help='Source file to output assembler for.',
                            metavar='<file>')

    def _run(self, args, environment):
        asm = _assembler_for_source_file(source.get_source_file(environment, args.source_paths[0]),
                                         args.verbose)

        if args.count:
            counter = OpcodeCounter()
            counter.count_in_string(asm)
            asm = counter.get_comment() + asm

        print(asm)
