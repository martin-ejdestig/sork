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

from typing import Any, Dict, List, Optional

from . import error


class Error(error.Error):
    pass


Config = Dict[str, Any]


# Need to explicitly check type with type() instead of using isinstance() since
# isinstance(True, int) is True. Bool values as integers should not be ok.
def _value_is(value: Any, type_: type) -> bool:
    return type(value) == type_  # pylint: disable=unidiomatic-typecheck


class Type:
    def __init__(self, type_: type) -> None:
        self._type = type_

    def verify(self, value: Any) -> bool:
        return _value_is(value, self._type)


class ListType(Type):
    def __init__(self, element_type, min_length: int = 0) -> None:
        super().__init__(list)
        self._element_type = element_type
        self._min_length = min_length

    def verify(self, value: Any) -> bool:
        return (super().verify(value) and
                len(value) >= self._min_length and
                all(_value_is(v, self._element_type) for v in value))


class Value:
    def __init__(self, default: Any, types: Optional[List[Type]] = None) -> None:
        if isinstance(default, dict):
            if not all(isinstance(k, str) and isinstance(v, Value) for k, v in default.items()):
                raise ValueError('Dictionary must have string as keys and Value as values.')

        if not types:
            if isinstance(default, list):
                if not default:
                    raise ValueError('List with no elements must explicitly set types.')
                types = [ListType(type(default[0]))]
            else:
                types = [Type(type(default))]

        self.default = default
        self.types = types

        if not self.verify(self.default):
            raise ValueError('Default does not match allowed types.')

    def verify(self, value: Any) -> bool:
        return any(t.verify(value) for t in self.types)


class Schema:
    def __init__(self, values: Dict[str, Value]) -> None:
        self._values = values

    def get_default(self) -> Config:
        def from_values(values: Dict[str, Value]) -> Config:
            default = {}

            for key, value in values.items():
                if isinstance(value.default, dict):
                    default[key] = from_values(value.default)
                else:
                    default[key] = value.default

            return default

        return from_values(self._values)

    def verify(self, config: Config):
        def verify_values(schema_values: Dict[str, Value],
                          config: Config,
                          parent_path: str):
            def full_path(key):
                return '{}.{}'.format(parent_path, key) if parent_path else key

            for key, value in config.items():
                if key not in schema_values:
                    raise Error('Unknown configuration key "{}"'.format(full_path(key)))

                schema_value = schema_values[key]

                if not schema_value.verify(value):
                    raise Error('Value for "{}" is not valid'.format(full_path(key)))

                if isinstance(schema_value.default, dict):
                    verify_values(schema_value.default, value, full_path(key))

        verify_values(self._values, config, None)


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


def create(path: str, schema: Schema) -> Config:
    try:
        config = _merge(schema.get_default(), _load(path))
        schema.verify(config)
    except Exception as exception:
        raise Error('{}: {}'.format(path, exception))

    return config
