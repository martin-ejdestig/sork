# This file is part of Sork.
#
# Copyright (C) 2017-2018 Martin Ejdestig <marejde@gmail.com>
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

import os
import unittest

from .. import environment


class AppendPathsTestCase(unittest.TestCase):
    PATHS1 = ['/foo/bar']
    PATHS1_STR = PATHS1[0]

    PATHS2 = ['/foo/bar', '/baz/qux']
    PATHS2_STR = os.pathsep.join(PATHS2)

    def test_unset_before(self):
        env = {}
        environment.append_paths(env, 'PATH', [])
        self.assertEqual(env, {})

        env = {}
        environment.append_paths(env, 'PATH', self.PATHS1)
        self.assertEqual(env, {'PATH': self.PATHS1_STR})

        env = {}
        environment.append_paths(env, 'PATH', self.PATHS2)
        self.assertEqual(env, {'PATH': self.PATHS2_STR})

    def test_empty_before(self):
        env = {'PATH': ''}
        environment.append_paths(env, 'PATH', [])
        self.assertEqual(env, {'PATH': ''})

        env = {'PATH': ''}
        environment.append_paths(env, 'PATH', self.PATHS1)
        self.assertEqual(env, {'PATH': self.PATHS1_STR})

        env = {'PATH': ''}
        environment.append_paths(env, 'PATH', self.PATHS2)
        self.assertEqual(env, {'PATH': self.PATHS2_STR})

    def test_set_one_before(self):
        default = '/abc/def'

        env = {'PATH': default}
        environment.append_paths(env, 'PATH', [])
        self.assertEqual(env, {'PATH': default})

        env = {'PATH': default}
        environment.append_paths(env, 'PATH', self.PATHS1)
        self.assertEqual(env, {'PATH': default + os.pathsep + self.PATHS1_STR})

        env = {'PATH': default}
        environment.append_paths(env, 'PATH', self.PATHS2)
        self.assertEqual(env, {'PATH': default + os.pathsep + self.PATHS2_STR})

    def test_set_two_before(self):
        default = '/abc/def' + os.pathsep + '/ghi/jkl'

        env = {'PATH': default}
        environment.append_paths(env, 'PATH', [])
        self.assertEqual(env, {'PATH': default})

        env = {'PATH': default}
        environment.append_paths(env, 'PATH', self.PATHS1)
        self.assertEqual(env, {'PATH': default + os.pathsep + self.PATHS1_STR})

        env = {'PATH': default}
        environment.append_paths(env, 'PATH', self.PATHS2)
        self.assertEqual(env, {'PATH': default + os.pathsep + self.PATHS2_STR})
