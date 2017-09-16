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

import argparse
import logging
import os
import sys

from . import arguments
from . import error
from . import paths
from .project import Project


def _path_in_project(args: argparse.Namespace) -> str:
    source_paths = args.source_paths if hasattr(args, 'source_paths') else None
    return source_paths[0] if source_paths else os.path.curdir


def _create_project(args: argparse.Namespace) -> Project:
    project_path = paths.find_project_path(_path_in_project(args))
    build_path = args.build_path or paths.find_build_path(project_path)
    return Project(project_path, build_path)


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s')

    arg_parser = arguments.Parser()
    args = arg_parser.parse_args()

    try:
        project = _create_project(args)
        args.command.run(args, project)
    except KeyboardInterrupt:
        pass
    except error.Error as exception:
        print(exception)
        sys.exit(1)
