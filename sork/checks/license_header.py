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

import itertools
import glob
import os
import re
import string

from .. import check


# TODO: Make it possible to set allowed start/end year in config (default to start year <= current
#       year and end year = current year).
#
# TODO: Make it possible to specify list of allowed authors in config.
#
# TODO: More informative error output than "invalid header". (diff? just print erroneous line #?)
#
# TODO: Maybe make it possible to specify a custom license text. E.g. if config['license'] does
#       not match any license in _LICENSES, see if it is a string containing $project, $year
#       and/or $author... something along those lines... Or maybe just check for a string longer
#       than X chars.
#
# TODO: Projects that contain multiple licenses are not handled. Allow for specifying list of
#       licenses in config and also handle detecting multiple COPYING*/LICENSE* files? Use
#       '(' + '|'.join(<list of header regexps>) + ')' when compiling regex to match against
#       multiple headers when/if implementing.
#
# TODO: Be less strict about line breaking in headers?


_LICENSES = {
    'apache2': {
        'content_pattern': r"\s*Apache License\s*\n"
                           r"\s*Version 2.0, January 2004",
        'header_lines': [
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
        ]
    },
    'gplv2': {
        'content_pattern': r"\s*GNU GENERAL PUBLIC LICENSE\s*\n"
                           r"\s*Version 2, June 1991",
        'header_lines': [
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
        ]
    },
    'gplv3': {
        'content_pattern': r"\s*GNU GENERAL PUBLIC LICENSE\s*\n"
                           r"\s*Version 3, 29 June 2007",
        'header_lines': [
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
        ]
    },
    'lgplv2': {
        'content_pattern': r"\s*GNU LIBRARY GENERAL PUBLIC LICENSE\s*\n"
                           r"\s*Version 2, June 1991",
        'header_lines': [
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
        ]
    },
    'lgplv2.1': {
        'content_pattern': r"\s*GNU LESSER GENERAL PUBLIC LICENSE\s*\n"
                           r"\s*Version 2.1, February 1999",
        'header_lines': [
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
        ]
    },
    'lgplv3': {
        'content_pattern': r"\s*GNU LESSER GENERAL PUBLIC LICENSE\s*\n"
                           r"\s*Version 3, 29 June 2007",
        'header_lines': [
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
        ]
    }
}

_LICENSE_BASE_FILE_NAMES = ['COPYING', 'LICENSE']


def _pattern_ignore_case(pattern):
    def ignore_case_if_alpha(char):
        return '[{}{}]'.format(char.upper(), char.lower()) if char.isalpha() else char

    return ''.join([ignore_case_if_alpha(char) for char in pattern])


def _find_license_paths(environment):
    patterns = [os.path.join(environment.project_path, _pattern_ignore_case(n + '*'))
                for n in _LICENSE_BASE_FILE_NAMES]

    paths = itertools.chain.from_iterable(glob.glob(p) for p in patterns)

    return list(paths)


def _determine_license_in_file(path):
    try:
        with open(path) as file:
            content = file.read()
    except OSError as error:
        raise check.Error(error)

    for key, value in _LICENSES.items():
        if re.match(value['content_pattern'], content):
            return key

    raise check.Error('Unknown license in {}.'.format(path))


def _detect_license(environment):
    paths = _find_license_paths(environment)
    if not paths:
        raise check.Error('Unable to find any license file(s) in {}.'.
                          format(environment.project_path))

    licenses = [_determine_license_in_file(path) for path in paths]

    if len(paths) == 1:
        return licenses[0]

    if len(paths) == 2 and 'gplv3' in licenses and 'lgplv3' in licenses:
        return 'lgplv3'

    raise check.Error('Unable to automatically determine license in {}.'.
                      format(environment.project_path))


def _get_header_lines(environment, license_key=None):
    if license_key:
        if license_key.lower() not in _LICENSES:
            raise check.Error('{} is an unknown license'.format(license_key))
        license_key = license_key.lower()
    else:
        license_key = _detect_license(environment)

    return _LICENSES[license_key]['header_lines']


def _join_header_lines(prefix, line_prefix, suffix, lines):
    def prepend_prefix(line):
        return line_prefix + line if line else line_prefix.rstrip()

    return ''.join([prefix, '\n'.join(prepend_prefix(l) for l in lines), suffix])


def _escape_regex_chars(unescaped):
    escaped = unescaped
    escaped = re.sub(r'\*', r'\*', escaped)
    escaped = re.sub(r'([()])', r'\\\1', escaped)
    return escaped


def _compile_license_regex(environment):
    config = environment.config['checks.license_header']

    template_str = _join_header_lines(config['prefix'],
                                      config['line_prefix'],
                                      config['suffix'],
                                      _get_header_lines(environment,
                                                        config['license']))

    template = string.Template(_escape_regex_chars(template_str))

    regex_str = template.safe_substitute(project=config['project'],
                                         year=r"[0-9]{4}(-[0-9]{4})?",
                                         author=r".+")
    try:
        return re.compile(regex_str, flags=re.DOTALL)
    except re.error:
        check.Error('Failed to compile regular expression for license header')


class LicenseHeaderCheck(check.Check):
    name = 'license_header'

    def __init__(self, environment):
        super().__init__(environment)
        self._license_regex = _compile_license_regex(environment)

    def check(self, source_file):
        if not self._license_regex.match(source_file.content):
            return '{}: error: invalid license header'.format(source_file.path)

        return ''