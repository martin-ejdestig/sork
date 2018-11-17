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

import itertools
import glob
import os
import re
import string

from typing import Dict, List, Optional, Pattern, Sequence

from .check import Check

from .. import error
from ..config import Config
from ..project import Project
from ..source import SourceFile


# TODO: More informative error output than "invalid header". (diff? just print erroneous line #?)


NAME = 'license_header'


class License:
    def __init__(self, name: str, content_pattern: str, header_lines: List[str]) -> None:
        self.name = name
        self.content_pattern = content_pattern
        self.header_lines = header_lines


_LICENSE_APACHE2 = \
    License('apache2',
            content_pattern=r"\s*Apache License\s*\n"
                            r"\s*Version 2.0, January 2004",
            header_lines=[
                'Copyright $year $author',
                '',
                'Licensed under the Apache License, Version 2.0 (the "License");',
                'you may not use this file except in compliance with the License.',
                'You may obtain a copy of the License at',
                '',
                '    http://www.apache.org/licenses/LICENSE-2.0',
                '',
                'Unless required by applicable law or agreed to in writing, software',
                'distributed under the License is distributed on an "AS IS" BASIS,',
                'WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.',
                'See the License for the specific language governing permissions and',
                'limitations under the License.'
            ])

_LICENSE_GPLV2 = \
    License('gplv2',
            content_pattern=r"\s*GNU GENERAL PUBLIC LICENSE\s*\n"
                            r"\s*Version 2, June 1991",
            header_lines=[
                'This file is part of $project.',
                '',
                'Copyright (C) $year $author',
                '',
                '$project is free software; you can redistribute it and/or modify',
                'it under the terms of the GNU General Public License as published by',
                'the Free Software Foundation; either version 2 of the License, or',
                '(at your option) any later version.',
                '',
                '$project is distributed in the hope that it will be useful,',
                'but WITHOUT ANY WARRANTY; without even the implied warranty of',
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the',
                'GNU General Public License for more details.',
                '',
                'You should have received a copy of the GNU General Public License',
                'along with $project. If not, see <http://www.gnu.org/licenses/>.'
            ])

_LICENSE_GPLV3 = \
    License('gplv3',
            content_pattern=r"\s*GNU GENERAL PUBLIC LICENSE\s*\n"
                            r"\s*Version 3, 29 June 2007",
            header_lines=[
                'This file is part of $project.',
                '',
                'Copyright (C) $year $author',
                '',
                '$project is free software: you can redistribute it and/or modify',
                'it under the terms of the GNU General Public License as published by',
                'the Free Software Foundation, either version 3 of the License, or',
                '(at your option) any later version.',
                '',
                '$project is distributed in the hope that it will be useful,',
                'but WITHOUT ANY WARRANTY; without even the implied warranty of',
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the',
                'GNU General Public License for more details.',
                '',
                'You should have received a copy of the GNU General Public License',
                'along with $project. If not, see <http://www.gnu.org/licenses/>.'
            ])

_LICENSE_LGPLV2 = \
    License('lgplv2',
            content_pattern=r"\s*GNU LIBRARY GENERAL PUBLIC LICENSE\s*\n"
                            r"\s*Version 2, June 1991",
            header_lines=[
                'This file is part of $project.',
                '',
                'Copyright (C) $year $author',
                '',
                '$project is free software; you can redistribute it and/or modify',
                'it under the terms of the GNU Library General Public License as published by',
                'the Free Software Foundation; either version 2 of the License, or',
                '(at your option) any later version.',
                '',
                '$project is distributed in the hope that it will be useful,',
                'but WITHOUT ANY WARRANTY; without even the implied warranty of',
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the',
                'GNU Library General Public License for more details.',
                '',
                'You should have received a copy of the GNU Library General Public License',
                'along with $project. If not, see <http://www.gnu.org/licenses/>.'
            ])

_LICENSE_LGPLV2_1 = \
    License('lgplv2.1',
            content_pattern=r"\s*GNU LESSER GENERAL PUBLIC LICENSE\s*\n"
                            r"\s*Version 2.1, February 1999",
            header_lines=[
                'This file is part of $project.',
                '',
                'Copyright (C) $year $author',
                '',
                '$project is free software; you can redistribute it and/or modify',
                'it under the terms of the GNU Lesser General Public License as published by',
                'the Free Software Foundation; either version 2.1 of the License, or',
                '(at your option) any later version.',
                '',
                '$project is distributed in the hope that it will be useful,',
                'but WITHOUT ANY WARRANTY; without even the implied warranty of',
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the',
                'GNU Lesser General Public License for more details.',
                '',
                'You should have received a copy of the GNU Lesser General Public License',
                'along with $project. If not, see <http://www.gnu.org/licenses/>.'
            ])

_LICENSE_LGPLV3 = \
    License('lgplv3',
            content_pattern=r"\s*GNU LESSER GENERAL PUBLIC LICENSE\s*\n"
                            r"\s*Version 3, 29 June 2007",
            header_lines=[
                'This file is part of $project.',
                '',
                'Copyright (C) $year $author',
                '',
                '$project is free software: you can redistribute it and/or modify',
                'it under the terms of the GNU Lesser General Public License as published by',
                'the Free Software Foundation, either version 3 of the License, or',
                '(at your option) any later version.',
                '',
                '$project is distributed in the hope that it will be useful,',
                'but WITHOUT ANY WARRANTY; without even the implied warranty of',
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the',
                'GNU Lesser General Public License for more details.',
                '',
                'You should have received a copy of the GNU Lesser General Public License',
                'along with $project. If not, see <http://www.gnu.org/licenses/>.'
            ])

_LICENSE_LIST: List[License] = [
    _LICENSE_APACHE2,
    _LICENSE_GPLV2,
    _LICENSE_GPLV3,
    _LICENSE_LGPLV2,
    _LICENSE_LGPLV2_1,
    _LICENSE_LGPLV3
]

_LICENSE_DICT: Dict[str, License] = {l.name: l for l in _LICENSE_LIST}

_LICENSE_BASE_FILE_NAMES = ['COPYING', 'LICENSE']


class Error(error.Error):
    pass


def _detect_license(project: Project) -> License:
    def ignore_case_if_alpha(char) -> str:
        return '[{}{}]'.format(char.upper(), char.lower()) if char.isalpha() else char

    def pattern_ignore_case(pattern: str) -> str:
        return ''.join([ignore_case_if_alpha(char) for char in pattern])

    def find_license_paths() -> List[str]:
        patterns = [os.path.join(project.path, pattern_ignore_case(n + '*'))
                    for n in _LICENSE_BASE_FILE_NAMES]

        paths = itertools.chain.from_iterable(glob.glob(p) for p in patterns)

        return list(paths)

    def determine_license_in_file(path: str) -> License:
        try:
            with open(path) as file:
                content = file.read()
        except OSError as exception:
            raise Error(exception)

        for license_ in _LICENSE_LIST:
            if re.match(license_.content_pattern, content):
                return license_

        raise Error('Unknown license in {}.'.format(path))

    paths = find_license_paths()
    if not paths:
        raise Error('Unable to find any license file(s) in \'{}\'.'. format(project.path))

    licenses = [determine_license_in_file(path) for path in paths]

    if len(licenses) == 1:
        return licenses[0]

    if len(licenses) == 2 and _LICENSE_GPLV3 in licenses and _LICENSE_LGPLV3 in licenses:
        return _LICENSE_LGPLV3

    raise Error('Unable to automatically determine license in \'{}\'.'. format(project.path))


def _compile_license_regex(project: Project, config: Config) -> Pattern:
    def get_header_lines() -> Sequence[str]:
        name_or_lines = config['license']

        if isinstance(name_or_lines, list):
            return name_or_lines

        if name_or_lines:
            name = name_or_lines.lower()
            if name not in _LICENSE_DICT:
                raise Error('{} is an unknown license'.format(name_or_lines))
            license_ = _LICENSE_DICT[name]
        else:
            license_ = _detect_license(project)

        return license_.header_lines

    def join_header_lines(lines: Sequence[str]) -> str:
        prefix = config['prefix']
        line_prefix = config['line_prefix']
        suffix = config['suffix']

        def prepend_prefix(line):
            return line_prefix + line if line else line_prefix.rstrip()

        return ''.join([prefix, '\n'.join(prepend_prefix(l) for l in lines), suffix])

    def escape_regex_chars(unescaped: str) -> str:
        escaped = unescaped
        escaped = re.sub(r'\*', r'\*', escaped)
        escaped = re.sub(r'([()])', r'\\\1', escaped)
        return escaped

    template_str = join_header_lines(get_header_lines())

    template = string.Template(escape_regex_chars(template_str))

    regex_str = template.safe_substitute(project=config['project'],
                                         year=r"[0-9]{4}(-[0-9]{4})?",
                                         author=r".+")
    try:
        return re.compile(regex_str, flags=re.DOTALL)
    except re.error:
        raise Error('Failed to compile regular expression for license header')


def create(project: Project) -> Check:
    config = project.config['checks.' + NAME]
    license_regex = _compile_license_regex(project, config)

    def run(source_file: SourceFile) -> Optional[str]:
        if not license_regex.match(source_file.content):
            return '{}: error: invalid license header'.format(source_file.path)

        return None

    return Check(NAME, run)
