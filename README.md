# Sork

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

- Python (version 3.2 or later)
- Clang (clang-format and clang-tidy)


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

By default Sork looks for a compilation database in build directories matching `path_to_project/*`,
`path_to_project/../name_of_project_directory*` and
`path_to_project/../build*/name_of_project_directory*`. Sork requires the path to be passed manually
on the command line if no or more than one database is found.


## Project configuration

Project specific configuration can be stored in a JSON file named `.sork` in the project root.
Detailed documentation for configuration relating to a specific command can be found in the
[Commands](#commands) section. JSON for default global configuration:

```json
{
    "source_paths": ["."]
}
```

- source_paths: List of paths relative to project root to traverse when looking for source files.
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

- clang_format: Runs [clang-format](http://clang.llvm.org/docs/ClangFormat.html). Used to check
  formatting.
- clang_tidy: Runs [clang-tidy](http://clang.llvm.org/extra/clang-tidy/index.html). Only invoked for
  source files that have an entry in the compilation database.
- include_guard: Verifies that include guards in header files are properly named. Currently
  requires include guards to be named according to the following format: &lt;PREFIX&gt;&lt;Upper
  case path of header with space, / and - replaced with underscore&gt;&lt;SUFFIX&gt;.

#### Configuration

```json
{
    "checks.include_guard": {
        "prefix": "",
        "suffix": "_H",
        "strip_paths": ["include", "src"]
    }
}
```

- checks.include_guard
  - prefix: String all include guard identifiers must start with. Usually set to something like
    PROJECT_NAME_. Defaults to the empty string.
  - suffix: String all include guard identifiers must end with.
  - strip_paths: Leading paths to remove from header path before inserting it between prefix and
    suffix.


## TODO

- Check that verifies that copyright/license header is correct (text, year, etc.).
- Implement --fix flag for check that fixes found errors if possible.
- Add regular expression in configuration for source files that should be excluded.
- Multiple recursive glob.glob() is slow on large repositories. E.g. it takes 2-3 minutes
  to find all source files in the Chromium repository both with and without a warm cache while it
  takes ~50 seconds with `find` and a cold cache and 3 seconds with a warm cache.
- Exit code other than 0 if analyze/check finds any errors or if asm cannot output assembler?
- More robust project root detection (check for more VCS dot directories, ... other ideas?)
- Add user specific configuration in $HOME/.config/ that lets user add search paths for how to find
  build directories. Want to avoid -bp/--build-path flag as much as possible.
- More tests.
- Add a setup.py. https://docs.python.org/3.5/distutils/setupscript.html
- --dump-config/-dc (a la clang-format)? Need to set default values instead of relying on fallback
  to get().
