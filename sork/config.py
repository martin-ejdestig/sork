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

import json


_DEFAULT_CONFIG = {
    'source_paths': ['.'],

    'checks.include_guard': {
        'prefix': '',
        'suffix': '_H',
        'strip_paths': ['include', 'src']
    }
}


class Error(Exception):
    pass


def _verify_config(config, default_config, parent_path=None):
    for key, value in config.items():
        full_path = '{}.{}'.format(parent_path, key) if parent_path else key

        if key not in default_config:
            raise Error('Unknown configuration key "{}"'.format(full_path))

        default_value = default_config[key]

        if not isinstance(value, type(default_value)):
            raise Error('Value for "{}" is of wrong type'.format(full_path))

        if isinstance(value, dict):
            _verify_config(value, default_value, full_path)
        elif isinstance(value, list):
            if value and default_value:
                if not all(isinstance(element, type(default_value[0])) for element in value):
                    raise Error('List element for "{}" is of wrong type'.format(full_path))


def _merge_configs(default_config, override_config):
    config = {}

    for key, value in override_config.items():
        if isinstance(value, dict):
            config[key] = _merge_configs(default_config[key], value)
        else:
            config[key] = value

    return {**default_config, **config}


def load_config(path):
    config = {}

    try:
        with open(path) as file:
            config = json.load(file)
    except FileNotFoundError:
        pass
    except Exception as exception:
        raise Error('Failed to load "{}": {}'.format(path, exception))

    _verify_config(config, _DEFAULT_CONFIG)

    return _merge_configs(_DEFAULT_CONFIG, config)
