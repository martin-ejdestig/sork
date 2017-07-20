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

from typing import Optional

from ..environment import Environment
from ..source import SourceFile


class Check(abc.ABC):
    NAME = ''

    def __init__(self, environment: Environment) -> None:
        super().__init__()
        self._environment = environment
        self._config = environment.config.get('checks.' + self.NAME) if self.NAME else None

    @abc.abstractmethod
    def check(self, source_file: SourceFile) -> Optional[str]:
        pass
