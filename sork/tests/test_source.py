# This file is part of Sork.
#
# Copyright (C) 2017 Martin Ejdestig <marejde@gmail.com>
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

from .test_case_with_tmp_dir import TestCaseWithTmpDir

from ..source import SourceFile
from ..project import Project


class SourceFileTestCase(TestCaseWithTmpDir):
    def test_compile_command(self):
        self.create_tmp_build_dir('build', comp_db=[
            {
                'directory': self.tmp_path('build'),
                'command': 'c++ -o foo.o -c ../foo.cpp',
                'file': '../foo.cpp'
            },
            {
                'directory': self.tmp_path('build'),
                'command': 'c++ -o bar.o -c ../bar.cpp',
                'file': '../bar.cpp'
            }
        ])

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            foo_src = SourceFile('foo.cpp', project)
            bar_src = SourceFile('bar.cpp', project)
            no_compile_command_src = SourceFile('has_no_compile_command.cpp', project)

            self.assertEqual(self.tmp_path('build'), foo_src.compile_command.work_dir)
            self.assertEqual('c++ -o foo.o -c ../foo.cpp', foo_src.compile_command.invokation)
            self.assertEqual('../foo.cpp', foo_src.compile_command.file)

            self.assertEqual(self.tmp_path('build'), bar_src.compile_command.work_dir)
            self.assertEqual('c++ -o bar.o -c ../bar.cpp', bar_src.compile_command.invokation)
            self.assertEqual('../bar.cpp', bar_src.compile_command.file)

            self.assertIsNone(no_compile_command_src.compile_command)

    def test_content(self):
        content = 'void foo()\n{\n}\n'
        self.create_tmp_file('src/foo.cpp', content)
        self.create_tmp_build_dir('build')

        with self.cd_tmp_dir():
            project = Project('.', 'build')
            src_file = SourceFile('src/foo.cpp', project)
            does_not_exist = SourceFile('src/does_not_exist.cpp', project)

            self.assertEqual(content, src_file.content)
            with self.assertRaisesRegex(FileNotFoundError, 'src/does_not_exist.cpp'):
                _ = does_not_exist.content

    def test_content_absolute_project_path(self):
        content = 'void foo()\n{\n}\n'
        self.create_tmp_file('src/foo.cpp', content)
        self.create_tmp_build_dir('build')

        project = Project(self.tmp_path('.'), self.tmp_path('build'))
        src_file = SourceFile('src/foo.cpp', project)
        does_not_exist = SourceFile('src/does_not_exist.cpp', project)

        self.assertEqual(content, src_file.content)
        with self.assertRaisesRegex(FileNotFoundError, 'src/does_not_exist.cpp'):
            _ = does_not_exist.content

    def test_is_header(self):
        self.create_tmp_build_dir('build')
        project = Project(self.tmp_path('.'), self.tmp_path('build'))

        self.assertTrue(SourceFile('abc.h', project).is_header)
        self.assertTrue(SourceFile('def.h.in', project).is_header)
        self.assertFalse(SourceFile('ghi.cpp', project).is_header)
        self.assertFalse(SourceFile('jkl.cpp.in', project).is_header)
        self.assertFalse(SourceFile('mno.c', project).is_header)
        self.assertFalse(SourceFile('pqr.c.in', project).is_header)
        self.assertFalse(SourceFile('stu', project).is_header)
        self.assertFalse(SourceFile('vxy.in', project).is_header)

    def test_stem(self):
        self.create_tmp_build_dir('build')
        project = Project(self.tmp_path('.'), self.tmp_path('build'))

        self.assertEqual('abc', SourceFile('abc.h', project).stem)
        self.assertEqual('def', SourceFile('def.h.in', project).stem)
        self.assertEqual('ghi', SourceFile('ghi.cpp', project).stem)
        self.assertEqual('jkl', SourceFile('jkl.cpp.in', project).stem)
        self.assertEqual('mno', SourceFile('mno.c', project).stem)
        self.assertEqual('pqr', SourceFile('pqr.c.in', project).stem)
        self.assertEqual('stu', SourceFile('stu', project).stem)
        self.assertEqual('vxy', SourceFile('vxy.in', project).stem)
