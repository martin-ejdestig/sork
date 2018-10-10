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

import abc

from typing import Optional

from ..project import Project
from ..source import SourceFile


class Check(abc.ABC):
    NAME = ''

    def __init__(self, project: Project) -> None:
        super().__init__()
        self._project = project

    @abc.abstractmethod
    def check(self, source_file: SourceFile) -> Optional[str]:
        pass
