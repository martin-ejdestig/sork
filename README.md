# Sork

[![License](http://img.shields.io/:License-GPLv3-blue.svg)](COPYING)

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


## Dependencies

- Python (version 3.5 or later)
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
(requires special flag) and [Meson](https://github.com/mesonbuild/meson) (database is generated
by default).

By default Sork looks for a compilation database in build directories matching:
- `path_to_project/*`
- `path_to_project/../name_of_project_directory*`
- `path_to_project/../build*/name_of_project_directory*`
- `path_to_project/../build-name_of_project_directory*`

Sork requires the path to be passed manually on the command line if no or more than one database is
found.


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

- source\_exclude: Regular expression for paths relative to project root to exclude. The value is
  passed to [re.compile](https://docs.python.org/library/re.html#re.compile) if set to something
  other than the empty string.
- source\_paths: List of paths relative to project root to traverse when looking for source files.
  Used when no source paths are passed on the command line.


## Commands

### analyze

Run Clang's static analyzer on source files that have an entry in the compilation database. Flags
not understood by Clang, GCC specific warning flags for instance, are filtered out.

### asm

Output assembler for compilation unit to standard output. Compiler and compilation flags are looked
up in the compilation database.

### check

Style check source files. Available checks:

- clang-format: Runs [clang-format](http://clang.llvm.org/docs/ClangFormat.html). Used to check
  formatting.
- clang-tidy: Runs [clang-tidy](http://clang.llvm.org/extra/clang-tidy/index.html). Only invoked for
  source files that have an entry in the compilation database.
- include\_guard: Verifies that include guards in header files are properly named. Currently
  requires include guards to be named according to the following format: &lt;PREFIX&gt;&lt;Upper
  case path of header with space, / and - replaced with underscore&gt;&lt;SUFFIX&gt;.
- license\_header: Checks that all source files have a correct license header.

#### Configuration

```json
{
    "checks": "",
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

- checks: Comma separated string of checks to perform. Defaults to all checks if the empty string.
  Prepend - to disable a check. Regular expressions may be used. All checks except foo: "-foo".
  Checks starting with clang- not containing bar: "clang-.\*,-.\*bar.\*" . Can be overridden from
  command line.
- checks.include\_guard:
  - prefix: String all include guard identifiers must start with. Usually set to something like
    PROJECT\_NAME\_. Defaults to the empty string.
  - suffix: String all include guard identifiers must end with.
  - strip\_paths: Leading paths to remove from header path before inserting it between prefix and
    suffix.
- checks.license\_header:
  - license: License used in project. If set to the empty string (the default) Sork tries to detect
    the license automatically by examining files matching COPYING\* and LICENSE\* in the project
    root (case is ignored). List of licenses currently recognized: Apache2, GPLv2, GPLv3, LGPLv2,
    LGPLv2.1 and LGPLv3. Value is case insensitive.
  - project: String to insert for project in license header.
  - prefix: String to insert before license text. Defaults to "/\*\*\\n" .
  - line\_prefix: String to insert before each line in license text. Defaults to " \* ".
  - suffix: String to insert after license text. Defaults to "\\n \*/\\n".


## Build system targets example

If you have an IDE or editor that can detect targets in your build system and/or makes build error
output in the format `<file>:<line>[:<column>]:<error message>` clickable you may want to add some
convenience targets that use Sork. If you use Git you may also want to add Sork as a submodule so
that it is readily available. The following example shows how to add targets for
[Meson](https://github.com/mesonbuild/meson) but it should be similar in any other build system.

In your project root run:

```shell
git submodule add https://github.com/martin-ejdestig/sork external/sork
```

Open `external/meson.build` in an editor and enter:

```
sork = find_program('sork/sork.py')
run_target('analyze', command : [sork, '--build-path', meson.build_root(), 'analyze', meson.source_root()])
run_target('style_check', command : [sork, '--build-path', meson.build_root(), 'check', meson.source_root()])
```

And add `subdir('external')` in you root `meson.build` if Sork is the first external component you
add. Then commit everything. You should now have two build targets called `analyze` and
`style_check` available that automatically use the correct build directory.


## TODO

- Implement --fix flag for check that fixes found errors if possible.
- Multiple recursive glob.glob() is slow on large repositories. E.g. it takes 2-3 minutes
  to find all source files in the Chromium repository both with and without a warm cache while it
  takes ~50 seconds with `find` and a cold cache and 3 seconds with a warm cache.
- More robust project root detection (check for more VCS dot directories, ... other ideas?)
- Add user specific configuration in $HOME/.config/ that lets user add search paths for how to find
  build directories. Want to avoid -bp/--build-path flag as much as possible.
- More tests.
- Add a setup.py. https://docs.python.org/3.5/distutils/setupscript.html
