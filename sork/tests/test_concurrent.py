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

import threading
import time
import unittest

from .. import concurrent


class ForEachTestCase(unittest.TestCase):
    def test_called_for_all(self):
        lock = threading.Lock()
        called = [False] * 10

        def set_called(index):
            with lock:
                called[index] = True

        concurrent.for_each(set_called, range(len(called)))

        self.assertTrue(all(called))

    def test_exception_reraised(self):
        def check_value(value):
            if value == 8:
                raise ValueError('bar')

        with self.assertRaises(ValueError) as ctx:
            concurrent.for_each(check_value, range(10))

        self.assertEqual(ctx.exception.args[0], 'bar')

    def test_not_called_in_main_thread(self):
        lock = threading.Lock()
        thread_ids = set()

        def add_thread_id(_):
            with lock:
                thread_ids.add(threading.get_ident())

        concurrent.for_each(add_thread_id, range(10))

        self.assertNotIn(threading.get_ident(), thread_ids)

    def test_num_threads(self):
        def threads_used(num_threads):
            lock = threading.Lock()
            thread_ids = set()

            def add_thread_id_and_wait(_):
                with lock:
                    thread_ids.add(threading.get_ident())
                time.sleep(0.001)

            concurrent.for_each(add_thread_id_and_wait,
                                range(num_threads * 2),
                                num_threads=num_threads)

            return len(thread_ids)

        self.assertLessEqual(threads_used(2), 2)
        self.assertLessEqual(threads_used(4), 4)
        self.assertLessEqual(threads_used(8), 8)
