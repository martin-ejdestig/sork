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

import abc


class Error(Exception):
    pass


class Command(abc.ABC):
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def add_arg_subparser(self, subparsers):
        pass

    def _create_arg_subparser(self, subparsers, name, aliases=None, arg_help=None):
        parser = subparsers.add_parser(name,
                                       aliases=aliases if aliases else [],
                                       help=arg_help)

        parser.set_defaults(run_command=self._run)

        return parser

    @abc.abstractmethod
    def _run(self, args, environment):
        pass
