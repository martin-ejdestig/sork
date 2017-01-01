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

import string


def index_to_line_and_column(text, index):
    if index < 0 or index >= len(text):
        raise ValueError('index must be >= 0 and < len(text)')

    line = 1
    column = 1

    for line_length in (len(line) for line in text.splitlines(True)):
        if index < line_length:
            column = index + 1
            break
        index -= line_length
        line += 1

    return (line, column)


def rstrip_single_char(to_strip, chars=string.whitespace):
    return to_strip[:-1] if to_strip.endswith(tuple(chars)) else to_strip
