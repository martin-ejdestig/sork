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

from typing import Optional

from . import check

from ..source import SourceFile


_CLANG_TIDY_NOISE_LINES = [
    r"[0-9]+ warnings? (and [0-9]+ errors? )?generated.",

    r"Suppressed [0-9]+ warnings? \([0-9]+ in non-user code(, [0-9]+ NOLINT)?\).",

    r"Use -header-filter=.* to display errors from all non-system headers.( Use -system-headers "
    r"to display errors from system headers as well.)?"
]

_CLANG_TIDY_NOISE_REGEX = re.compile('(?m)^(' + '|'.join(_CLANG_TIDY_NOISE_LINES) + ')$')


class ClangTidyCheck(check.Check):
    NAME = 'clang-tidy'

    def check(self, source_file: SourceFile) -> Optional[str]:
        if not source_file.compile_command:
            return None

        args = re.sub(r"^\S+ ", 'clang-tidy {} -- '.format(source_file.compile_command.file),
                      source_file.compile_command.invokation)
        args = re.sub(r" '?-W[a-z0-9-=]+'?", '', args)

        with subprocess.Popen(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True,
                              cwd=source_file.compile_command.work_dir,
                              env=source_file.project.command_env_vars(),
                              universal_newlines=True) as process:
            output = process.communicate()[0]

        return _CLANG_TIDY_NOISE_REGEX.sub('', output).strip()
