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

import os
import re
import subprocess

from typing import Optional

from .check import Check

from ..project import Project
from ..source import SourceFile


NAME = 'clang-tidy'

_CLANG_TIDY_NOISE_LINES = [
    r"[0-9]+ warnings? (and [0-9]+ errors? )?generated.",

    r"Suppressed [0-9]+ warnings? \([0-9]+ in non-user code(, [0-9]+ NOLINT)?"
    r"(, [0-9]+ with check filters)?\).",

    r"Use -header-filter=.* to display errors from all non-system headers.( Use -system-headers "
    r"to display errors from system headers as well.)?",

    # TODO: Remove once https://bugs.llvm.org/show_bug.cgi?id=46752 is fixed.
    r"warning: invalid case style for template parameter 'expr-type' "
    r"\[readability-identifier-naming\]"
]

_CLANG_TIDY_NOISE_REGEX = re.compile('(?m)^(' + '|'.join(_CLANG_TIDY_NOISE_LINES) + ')$')


# Current working directory matters when clang-tidy uses HeaderFilterRegex to
# determine if errors from headers should be displayed or not.
#
# Need to prepend relative path from build directory to project directory if
# relative paths are used in compilation commands (Meson). The absolute path
# needs to be prepended if absolute paths are used in compilation commands
# (CMake).
#
# TODO: Can this be removed? See https://bugs.llvm.org/show_bug.cgi?id=37281
#       for clang-tidy bug.
def _header_filter_override(source_file: SourceFile) -> Optional[str]:
    assert source_file.compile_command

    def config_header_filter(source_file: SourceFile) -> Optional[str]:
        config_path = os.path.join(source_file.project.path, '.clang-tidy')

        if not os.path.exists(config_path):
            return None

        with open(config_path, 'r') as file:
            line = next((l for l in file.readlines() if l.startswith('HeaderFilterRegex')), '')

        split = line.split(':', maxsplit=1)

        return split[1].strip('\n "\'') if len(split) == 2 else None

    if os.path.isabs(source_file.compile_command.file):
        path = source_file.project.path
    else:
        path = os.path.relpath(source_file.project.path,
                               start=source_file.compile_command.work_dir)
        if path == os.path.curdir:
            return None

    header_filter = config_header_filter(source_file)
    if not header_filter:
        return None

    return re.sub(r"(\^?)([^|]+)", r"\1" + path + r"/\2", header_filter)


def _compiler_exe_replacement(source_file: SourceFile) -> str:
    assert source_file.compile_command

    args = ['clang-tidy']

    header_filter_override = _header_filter_override(source_file)
    if header_filter_override:
        args += ['-header-filter=\'' + header_filter_override + '\'']

    args += [source_file.compile_command.file, '--']

    return ' '.join(args)


def create(_: Project) -> Check:
    def run(source_file: SourceFile) -> Optional[str]:
        if not source_file.compile_command:
            return None

        args = re.sub(r"^\S+ ", _compiler_exe_replacement(source_file) + ' ',
                      source_file.compile_command.invocation)
        args = re.sub(r" '?-W[a-z0-9-=]+'?", '', args)

        # clang-tidy >= 6.0 outputs:
        #
        # error: unknown argument: '-pipe' [clang-diagnostic-error]
        #
        # When "-Xclang -fcolor-diagnostics -pipe" is used in compilation command.
        # Happens when e.g. specifying CXX=clang++ with Meson.
        # "-fdiagnostics-color=always -pipe" that is generated when using GCC is
        # not an issue. Remove -pipe until bug is fixed in clang-tidy. See
        # https://bugs.llvm.org/show_bug.cgi?id=37315 .
        args = re.sub(r" '?-pipe'?", '', args)

        result = subprocess.run(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=True,
                                cwd=source_file.compile_command.work_dir,
                                universal_newlines=True)

        return _CLANG_TIDY_NOISE_REGEX.sub('', result.stdout).strip() or None

    return Check(NAME, run)
