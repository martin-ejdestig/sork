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

import json

from typing import Any, Dict

import jsonschema

from . import error


Config = Dict[str, Any]


def _merge(default_config: Config, override_config: Config) -> Config:
    config = {}

    for key, value in override_config.items():
        if isinstance(value, dict):
            config[key] = _merge(default_config[key], value)
        else:
            config[key] = value

    return {**default_config, **config}


def _load(path: str) -> Config:
    try:
        with open(path) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def create(path: str, default: Config, schema: Dict) -> Config:
    try:
        config = _merge(default, _load(path))
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as exception:
        raise error.Error('{}: {}'.format(path, exception.message))
    except Exception as exception:
        raise error.Error('{}: {}'.format(path, exception))

    return config
