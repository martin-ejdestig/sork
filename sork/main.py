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

import logging
import sys

from . import arguments
from . import error
from . import paths
from .project import Project


def main() -> None:
    logging.basicConfig(format='%(levelname)s: %(message)s')

    args = arguments.parse()

    try:
        project_path = paths.find_project_path(arguments.path_in_project(args))
        build_path = args.build_path or paths.find_build_path(project_path)
        project = Project(project_path, build_path)
        args.run_command(args, project)
    except KeyboardInterrupt:
        pass
    except error.Error as exception:
        print(exception)
        sys.exit(1)
