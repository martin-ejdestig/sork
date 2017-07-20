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

from . import error


_DEFAULT_CONFIG = {
    'source_exclude': '',
    'source_paths': ['.'],

    'checks': [],
    'checks.include_guard': {
        'prefix': '',
        'suffix': '_H',
        'strip_paths': ['include', 'src']
    },
    'checks.license_header': {
        'license': '',
        'project': '',
        'prefix': '/**\n',
        'line_prefix': ' * ',
        'suffix': '\n */\n'
    }
}


def _verify_config(config, default_config, parent_path=None):
    def full_path(key):
        return '{}.{}'.format(parent_path, key) if parent_path else key

    for key, value in config.items():
        if key not in default_config:
            raise error.Error('Unknown configuration key "{}"'.format(full_path(key)))

        default_value = default_config[key]

        if not isinstance(value, type(default_value)):
            raise error.Error('Value for "{}" is of wrong type'.format(full_path(key)))

        if isinstance(value, dict):
            _verify_config(value, default_value, full_path(key))
        elif isinstance(value, list):
            if value and default_value:
                if not all(isinstance(element, type(default_value[0])) for element in value):
                    raise error.Error('List element for "{}" is of wrong type'.
                                      format(full_path(key)))


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
        _verify_config(config, _DEFAULT_CONFIG)
    except FileNotFoundError:
        pass
    except Exception as exception:
        raise error.Error('{}: {}'.format(path, exception))

    return _merge_configs(_DEFAULT_CONFIG, config)
