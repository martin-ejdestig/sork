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

import abc
import argparse

from typing import List, Optional

from ..project import Project


class Command(abc.ABC):
    def __init__(self,
                 name,
                 aliases: Optional[List[str]] = None,
                 arg_help: Optional[str] = None) -> None:
        self._name = name
        self._aliases = aliases
        self._arg_help = arg_help

    def add_argparse_subparser(self, subparsers):
        parser = subparsers.add_parser(self._name,
                                       aliases=self._aliases if self._aliases else [],
                                       help=self._arg_help)

        parser.set_defaults(command=self)

        self._add_argparse_arguments(parser)

    @abc.abstractmethod
    def _add_argparse_arguments(self, parser: argparse.ArgumentParser):
        pass

    @abc.abstractmethod
    def run(self, args: argparse.Namespace, project: Project):
        pass
