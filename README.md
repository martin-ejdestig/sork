# Sork

[![License](http://img.shields.io/:License-GPLv3+-blue.svg)](COPYING)

Sork is a program that performs various operations on source files in a C/C++ project. See
[Commands](#commands) for a list of available commands.

Example that [checks](#check) all source files in the folder `src/lib/bar` of the project "foo" and
finds an error in the naming of a header include guard:

```shell
$ sork check ~/Source/foo/src/lib/bar
src/lib/bar/baz.h:53:11: error: include guard name should be FOO_LIB_BAR_BAZ_H
[18/18] Checking source. Done.
$
```


## Table of contents

- [Dependencies](#dependencies)
- [Installing from source](#installing-from-source)
- [Project root path detection](#project-root-path-detection)
- [Build directory and the compilation database](#build-directory-and-the-compilation-database)
- [Project configuration](#project-configuration)
- [Command line usage](#command-line-usage)
- [Commands](#commands)
  - [analyze](#analyze)
  - [asm](#asm)
  - [check](#check)
- [Build system targets examples](#build-system-targets-examples)
  - [Meson](#meson)
  - [CMake](#cmake)
- [TODO](#todo)


## Dependencies

- Python (version 3.6 or later)
- Clang (clang-format, clang-tidy and static analyzer)


## Installing from source

You can run Sork directly from a git checkout. For convenience you might want to create a link to
`sork.py` in one of your `PATH` directories, e.g. if you are standing in the Sork source root and
`~/.local/bin` is in your `PATH` run:

```shell
ln -s $(pwd)/sork.py ~/.local/bin/sork
```

Adding a `setup.py` is on the [TODO list](#todo).


## Project root path detection

When invoking Sork it tries to find the root directory of the project. By default it starts in the
current working directory and traverses the directory hierarchy upward until it finds a `.sork` or
VCS dot directory (only `.git` is supported at the moment). If a path is specified on the command
line this path is used as a starting location instead of the current working directory.


## Build directory and the compilation database

Sork often needs to know how source files are compiled. For this purpose, Sork relies on the
availability of a [compilation database](http://clang.llvm.org/docs/JSONCompilationDatabase.html).
Some build systems capable of generating a compilation database are [CMake](https://cmake.org)
(pass `-DCMAKE_EXPORT_COMPILE_COMMANDS=1` when invoking CMake) and
[Meson](https://github.com/mesonbuild/meson) (database is generated by default).

By default Sork looks for a compilation database in build directories matching:
- `path_to_project/*`
- `path_to_project/../name_of_project_directory*`
- `path_to_project/../build*/name_of_project_directory*`
- `path_to_project/../build-name_of_project_directory*`

For example, if a project is located in `~/Source/foo` all of the following build directories will
be detected automatically:
- `~/Source/foo/build`
- `~/Source/foo/build_release`
- `~/Source/foo-build`
- `~/Source/foo-build_release`
- `~/Source/build/foo`
- `~/Source/build/foo_release`
- `~/Source/build-foo`
- `~/Source/build-foo_release`

Sork requires the path to be passed manually on the command line if no or more than one database is
found. See [Build system targets examples](#build-system-targets-examples) for how to add build
targets that automatically pass the correct build path.


## Project configuration

Project specific configuration can be stored in a JSON file named `.sork` in the project root.
Detailed documentation for configuration relating to a specific command can be found in the
[Commands](#commands) section. JSON for default global configuration:

```json
{
    "source_exclude": "",
    "source_paths": ["."]
}
```

- `source_exclude`: Regular expression for paths relative to project root to exclude. The value is
  passed to [re.compile](https://docs.python.org/library/re.html#re.compile) if set to something
  other than the empty string.
- `source_paths`: List of paths relative to project root to traverse when looking for source files.
  Used when no source paths are passed on the command line.


## Command line usage

See the [Commands](#commands) section for command specific arguments.

```
sork [-h] [-bp <path>] [-j N] [-v] <command> ...

positional arguments:
  <command>             -h or --help after <command> for more help
    analyze             run static analyzer
    asm (assembler)     output assembler for compilation unit
    check               style check source code

optional arguments:
  -h, --help            show this help message and exit
  -bp <path>, --build-path <path>
                        Path to build directory, automatically detected if
                        possible.
  -j N, --jobs N        Run N jobs in parallel. Defaults to number of logical
                        cores (8 detected).
  -v, --verbose         More verbose output.
```


## Commands

### analyze

Run Clang's static analyzer on source files that have an entry in the
[compilation database](#build-directory-and-the-compilation-database). Flags not understood by
Clang, GCC specific warning flags for instance, are filtered out.

Command line usage:
```
sork analyze [-h] [<path> [<path> ...]]

positional arguments:
  <path>      Analyze path(s). Directories are recursed. All source code in
              project, subject to configuration in .sork, is analyzed if no
              <path> is passed or if only <path> passed is the project's root.

optional arguments:
  -h, --help  show this help message and exit
```

### asm

Output assembler for compilation unit to standard output. Compiler and compilation flags are looked
up in the [compilation database](#build-directory-and-the-compilation-database).

Command line usage:
```
sork asm [-h] [-c] [-va] <file>

positional arguments:
  <file>              Source file to output assembler for.

optional arguments:
  -h, --help          show this help message and exit
  -c, --count         Count occurance of different opcodes per global label
                      and in total if there is more than one global label.
                      Result is printed as a comment before the generated
                      assembly.
  -va, --verbose-asm  Tell compiler to output verbose assembler.
```

### check

Style check source files. Available checks:

- `clang-format`: Runs [clang-format](http://clang.llvm.org/docs/ClangFormat.html). Used to check
  formatting.
- `clang-tidy`: Runs [clang-tidy](http://clang.llvm.org/extra/clang-tidy/index.html). Only invoked
  for source files that have an entry in the
  [compilation database](#build-directory-and-the-compilation-database).
- `include_guard`: Verifies that include guards in header files are properly named. Currently
  requires include guards to be named according to the following format: &lt;PREFIX&gt;&lt;Upper
  case path of header with space, / and - replaced with underscore&gt;&lt;SUFFIX&gt;.
- `license_header`: Checks that all source files have a correct license header.

Command line usage:
```
sork check [-h] [-c <checks>] [<path> [<path> ...]]

positional arguments:
  <path>                Check path(s). Directories are recursed. All source
                        code in project, subject to configuration in .sork, is
                        checked if no <path> is passed or if only <path>
                        passed is the project's root.

optional arguments:
  -h, --help            show this help message and exit
  -c <checks>, --checks <checks>
                        Comma separated list of checks to perform. Overrides
                        configuration in .sork. Prepend - to disable a check.
                        Regular expressions may be used. All checks except
                        foo: --checks=-foo . Checks starting with clang-:
                        --checks=clang-.* .
```

Configuration:
```json
{
    "checks": ["clang-format", "clang-tidy", "include_guard", "license_header"],
    "checks.include_guard": {
        "prefix": "",
        "suffix": "_H",
        "strip_paths": ["include", "src"]
    },
    "checks.license_header": {
        "license": "",
        "project": "",
        "prefix": "/**\n",
        "line_prefix": " * ",
        "suffix": "\n */\n"
    }
}
```

- `checks`: Array of checks to perform. Defaults to all available checks. Prepend - to name of check
  to disable it. Regular expressions may be used. All checks are enabled if array is empty. All
  checks except foo: ["-foo"]. Checks starting with clang- not containing bar:
  ["clang-.\*", "-.\*bar.\*"] . Can be overridden from command line.
- `checks.include_guard`:
  - `prefix`: String all include guard identifiers must start with. Usually set to something like
    PROJECT\_NAME\_. Defaults to the empty string.
  - `suffix`: String all include guard identifiers must end with.
  - `strip_paths`: Leading paths to remove from header path before inserting it between prefix and
    suffix.
- `checks.license_header`:
  - `license`: License used in project. If set to the empty string (the default) Sork tries to
    detect the license automatically by examining files matching COPYING\* and LICENSE\* in the
    project root (case is ignored). List of licenses currently recognized: Apache2, GPLv2, GPLv3,
    LGPLv2, LGPLv2.1 and LGPLv3. Value is case insensitive. A custom license can be specified by
    setting the value to a list of strings. Each element in the list is a line. Lines should not
    end with newlines.
  - `project`: String to insert for project in license header.
  - `prefix`: String to insert before license text. Defaults to "/\*\*\\n" .
  - `line_prefix`: String to insert before each line in license text. Defaults to " \* ".
  - `suffix`: String to insert after license text. Defaults to "\\n \*/\\n".


## Build system targets examples

If you have an IDE or editor that can detect targets in your build system and/or makes build error
output in the format `<file>:<line>[:<column>]:<error message>` clickable you may want to add some
convenience targets that use Sork. The build path will also be detected automatically even if it is
not located in one of the [default locations](#build-directory-and-the-compilation-database).

The examples below will give you two build targets called `analyze` and `style_check` that runs the
[analyze](#analyze) and [check](#check) commands respectively.

You will have to adjust the program paths in the examples below if you have not added Sork to your
PATH as [descriped above](#installing-from-source) or if you have added Sork to your project as e.g.
a Git submodule.

### Meson

```
sork = find_program('sork')
run_target('analyze', command : [sork, '--build-path', meson.build_root(), 'analyze', meson.source_root()])
run_target('style_check', command : [sork, '--build-path', meson.build_root(), 'check', meson.source_root()])
```

### CMake

```
find_program(SORK sork)
if(NOT SORK)
	message(FATAL_ERROR "sork not found")
endif()
add_custom_target(analyze USES_TERMINAL COMMAND ${SORK} --build-path ${CMAKE_BINARY_DIR} analyze ${CMAKE_SOURCE_DIR})
add_custom_target(style_check USES_TERMINAL COMMAND ${SORK} --build-path ${CMAKE_BINARY_DIR} check ${CMAKE_SOURCE_DIR})
```

You must make sure CMake is invoked with `-DCMAKE_EXPORT_COMPILE_COMMANDS=1` for it to generate a
[compilation database](#build-directory-and-the-compilation-database) in the build directory.


## TODO

- Add a --revision/-r &lt;git range/rev&gt; flag for only checking/analyzing files/lines changed in
  range/rev.
- Implement --fix flag for check that fixes found errors if possible.
- More robust project root detection (check for more VCS dot directories, ... other ideas?)
- Add user specific configuration in $HOME/.config/ that lets user add search paths for how to find
  build directories. Want to avoid -bp/--build-path flag as much as possible.
- More tests.
- Add a setup.py. https://docs.python.org/3.5/distutils/setupscript.html
