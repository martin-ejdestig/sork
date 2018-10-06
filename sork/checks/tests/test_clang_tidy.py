# This file is part of Sork.
#
# Copyright (C) 2018 Martin Ejdestig <marejde@gmail.com>
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

import enum
import os

from typing import Any, Dict, List, Optional, Tuple

from ...project import Project
from ...source import SourceFile
from ...tests.test_case_with_tmp_dir import TestCaseWithTmpDir

from ..clang_tidy import ClangTidyCheck


class ClangTidyBaseTestCase(TestCaseWithTmpDir):
    def _create(self,
                project_path: str,
                build_path: str,
                comp_db: List[Dict[str, Any]]) -> Tuple[Project, ClangTidyCheck]:
        self.create_tmp_build_dir(build_path, comp_db=comp_db)
        project = Project(self.tmp_path(project_path), self.tmp_path(build_path))
        return project, ClangTidyCheck(project)

    def _create_source(self, project: Project, path: str, src_lines: List[str]) -> SourceFile:
        self.create_tmp_file(os.path.join(project.path, path), src_lines)
        return SourceFile(path, project)

    def _create_header(self, project, path: str, header_lines: List[str]):
        self.create_tmp_file(os.path.join(project.path, path), header_lines)

    def _create_dot_clang_tidy(self, project: Project, lines: List[str]):
        self.create_tmp_file(os.path.join(project.path, '.clang-tidy'), lines)


class ClangTidyTestCase(ClangTidyBaseTestCase):
    def test_no_error_returns_none(self):
        project, check = self._create('.', 'build', comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self._create_source(project, 'src/foo.cpp', ['int *p = nullptr;'])
        self._create_dot_clang_tidy(project, ['Checks: "modernize-use-nullptr"'])

        self.assertIsNone(check.check(src))

    def test_error_position_in_output(self):
        project, check = self._create('.', 'build', comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self._create_source(project, 'src/foo.cpp', ['int *p = 0;'])
        self._create_dot_clang_tidy(project, ['Checks: "modernize-use-nullptr"'])

        self.assertIn('src/foo.cpp:1:10', check.check(src))

    def test_source_without_compile_command_is_ignored(self):
        project, check = self._create('.', 'build', comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self._create_source(project, 'src/bar.cpp', ['int *p = 0;'])
        self._create_dot_clang_tidy(project, ['Checks: "modernize-use-nullptr"'])

        self.assertIsNone(check.check(src))

    def test_gcc_specific_warning_flags_ignored(self):
        project, check = self._create('.', 'build', comp_db=[{
            'directory': self.tmp_path('build'),
            'command': 'g++ -Wsuggest-override -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self._create_source(project, 'src/foo.cpp', [''])

        self.assertIsNone(check.check(src))

    def test_absolute_compiler_path_replaced_correctly(self):
        project, check = self._create('.', 'build', comp_db=[{
            'directory': self.tmp_path('build'),
            'command': '/usr/bin/c++ -o src/foo.o -c ../src/foo.cpp',
            'file': '../src/foo.cpp'
        }])
        src = self._create_source(project, 'src/foo.cpp', ['int *p = 0;'])
        self._create_dot_clang_tidy(project, ['Checks: "modernize-use-nullptr"'])

        self.assertIn('src/foo.cpp:1:10', check.check(src))


class Headers(enum.Flag):
    NONE = 0
    PRIVATE = enum.auto()
    PUBLIC = enum.auto()
    EXTERNAL = enum.auto()


class ClangTidyHeaderFilterTestCase(ClangTidyBaseTestCase):
    def _comp_db(self,
                 project_path: str,
                 build_path: str,
                 relative_paths: bool) -> List[Dict[str, Any]]:
        if relative_paths:
            path = os.path.relpath(project_path, start=build_path)  # What Meson does.
        else:
            path = self.tmp_path(project_path)  # What CMake does.

        includes = f'-I{path}/src -I{path}/include -I{path}/external/project/include'

        return [{
            'directory': self.tmp_path(build_path),
            'command': f'c++ {includes} -o src/bar.cpp.o -c {path}/src/bar.cpp',
            'file': f'{path}/src/bar.cpp'
        }]

    def _run_check(self,  # pylint: disable=too-many-arguments
                   expected_headers_in_output: Headers,
                   header_filter: Optional[str],
                   project_path: str,
                   build_path: str,
                   relative_comp_db_paths: bool):
        comp_db = self._comp_db(project_path, build_path, relative_paths=relative_comp_db_paths)
        project, check = self._create(project_path, build_path, comp_db)

        src = self._create_source(project, 'src/bar.cpp', [
            '#include <external_project.h>',
            '#include "public.h"',
            '#include "private.h"'
        ])

        def header_lines(guard: str, namespace: str, clazz: str) -> List[str]:
            return [
                '#ifndef ' + guard,
                '#define ' + guard,
                '',
                'namespace ' + namespace,
                '{',
                '    class ' + clazz,
                '    {',
                '        int baz_ = 0;',
                '        int qux = 0;',
                '    };',
                '}',
                '',
                '#endif'
            ]

        self._create_header(project,
                            'external/project/include/external_project.h',
                            header_lines('EXTERNAL_PROJECT_H',
                                         'ExternalProject',
                                         'Abc'))
        self._create_header(project,
                            'include/public.h',
                            header_lines('FOO_PUBLIC_H',
                                         'Foo',
                                         'Def'))
        self._create_header(project,
                            'src/private.h',
                            header_lines('FOO_PRIVATE_H',
                                         'Foo',
                                         'Ghi'))

        self._create_dot_clang_tidy(project, [
            'Checks: "readability-identifier-naming"',
            '' if header_filter is None else 'HeaderFilterRegex: \'' + header_filter + '\'',
            'CheckOptions:',
            '  - key:   readability-identifier-naming.PrivateMemberSuffix',
            '    value: \'_\'',
            ''
        ])

        output = check.check(src)

        if expected_headers_in_output:
            for path, header in [('src/private.h', Headers.PRIVATE),
                                 ('include/public.h', Headers.PUBLIC),
                                 ('external/project/include/external_project.h', Headers.EXTERNAL)]:
                if header & expected_headers_in_output:
                    self.assertRegex(output or '',
                                     path + r":9:13: .*qux.*readability-identifier-naming")
                else:
                    self.assertNotIn(path, output or '')
        else:
            self.assertIsNone(output)

    def _run_checks(self, headers_in_output: Headers, header_filter: Optional[str]):
        for project_path, build_path, relative_comp_db_paths in [('foo1', 'foo1/build', True),
                                                                 ('foo2', 'foo2-build', True),
                                                                 ('foo3', 'build/foo3', True),
                                                                 ('foo4', 'foo4/build', False),
                                                                 ('foo5', 'foo5-build', False),
                                                                 ('foo6', 'build/foo6', False)]:
            self._run_check(headers_in_output,
                            header_filter,
                            project_path,
                            build_path,
                            relative_comp_db_paths)

    def test_empty_string_filters_all_headers(self):
        self._run_checks(Headers.NONE, '')

    def test_not_present_filters_all_headers(self):
        self._run_checks(Headers.NONE, None)

    def test_single_dir_private_header(self):
        self._run_checks(Headers.PRIVATE, '^src/')

    def test_single_dir_public_header(self):
        self._run_checks(Headers.PUBLIC, '^include/')

    def test_multiple_dirs_private_and_public_headers(self):
        self._run_checks(Headers.PRIVATE | Headers.PUBLIC, '^include/|^src/')

    def test_dot_star_filters_nothing(self):
        self._run_checks(Headers.PRIVATE | Headers.PUBLIC | Headers.EXTERNAL, '.*')
