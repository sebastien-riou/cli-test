# cli-test
Test CLI programs as you document them (doctest for CLI)

## Concept
cli-test is a CLI tool which checks examples embedded within text files (source files, documentation files...).
It is loosely inspired by [doctest](https://docs.python.org/3/library/doctest.html) and [Sphinx doctest extension](https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/doctest.py).

It looks for the following markers:

- `cli-test-cmd`: that marker should be followed by a new line and the command line to run.
- `cli-test-cfg`: that marker should be followed by a new line and some options ovverrides. It is optional.
- `cli-test-out`: 
  - that marker should be followed by a new line and the expected output on `stdout`. 
  - alternatively that marker can be followed by the name of a file containing the expected content.
- `cli-test-err`: It is optional.
  - that marker should be followed by a new line and the expected output on `stderr`. 
  - alternatively that marker can be followed by the name of a file containing the expected content.
- `cli-test-end`: that marker marks the end of the previous section. 

By default, the following applies:

- Each example is independant and runs in a temporary directory.
- Examples may run concurrently.
- The environment variables are the same as for `cli-test`.
- The program runs with the same user that invoked `cli-test`.
- The program runs within the same python environment (but any program can be run).
- The program is killed after 30s of execution. Such timeout is considered as a fatal error and is reported as such.  

`cli-test` is a python module, it can be used as a library or as a CLI program. In both cases,
the following optional arguments allows to change the default behavior:

- `run-dir`: path to a directory.
- `path`: list of path to search the program.
- `env`: list of environment variables.
- `timeout`: custom value for timeout (human friendly notation, '10m' means 10 minutes for example).
- `setup`: execute a script before running each example.
- `global-setup`: execute a script before running the first example.
- `cleanup`: execute a script after running each example.
- `global-cleanup`: execute a script after running the last example.
- `cmp`: specifiy a python script which implement a custom comparison function (for example if you want to ignor timestamps in the output). that function should be called `compare` and take just two positional arguments `expected` and `actual`. `expected` comes from the `cli-test-out` or `cli-test-err` section and `actual` comes from the execution of the program under test, from `stdout` or `stderre` respectively.
- `seq`: should be 0 or 1. default is 0. run each example sequentially.
- `reuse`: should be 0 or 1. default is 0. run each example within the same common environment.
- `prefix`: change prefix for markers. default is 'cli-test-'. It should be something like 'my-prefix-' to have the marker 'my-prefix-cmd'.
- `hexdump`: should be 0 or 1. default is 0. output in `cli-test-out` is represented as an hexdump rather than the actual value.

Each example can override the settings by using the `cli-test-cfg` marker.
Each override must be on a separate line and follow the exact form `key=value`.
For example:
````
cli-test-cfg
    timeout=10s
    seq=1
    reuse=0
````

## Exact behavior

The following rules make the tool behavior precise and implementation-ready.

### Marker syntax

A source file is scanned for examples defined by markers:

- `cli-test-cmd`: starts a command block. The block continues until the next marker or end of file.
- `cli-test-cfg`: optional; configures the current example. It contains one override per line.
- `cli-test-out`: expected output on `stdout`.
- `cli-test-err`: optional; expected output on `stderr`.
- `cli-test-end`: closes the current example.

The scanner is line-based. A marker is recognized only when its exact text is found in the current section with the configured prefix, and it is case-sensitive.

### Config syntax

`cli-test-cfg` supports one setting per line using the format `name=value`.
Unknown keys are invalid and should stop parsing with an error.
Duplicate keys in the same block are invalid.

Supported keys include:

- `timeout`: duration string such as `10s`, `2m`, `500ms`
- `run-dir`: path to the working directory for the example
- `path`: list of directories to search for executables
- `env`: list of `NAME=value` pairs
- `setup`: script or command executed before the example
- `cleanup`: script or command executed after the example
- `seq`: `0` or `1`
- `reuse`: `0` or `1`
- `hexdump`: `0` or `1`
- `cmp`: Python script path containing a `compare(expected, actual)` function

Per-example values override the global defaults for that specific example only.

### Command execution

The command in a `cli-test-cmd` block is parsed into an argument list and executed with `shell=False`.
The command string is tokenized using the platform's standard shell-splitting rules:

- on POSIX systems, use `shlex.split(command, posix=True)`
- on Windows, use the equivalent Windows-aware splitting rules

The resulting argument vector is passed to `subprocess.run` without invoking a shell, so shell features such as pipes, redirections, `&&`, and `||` are not interpreted by `cli-test` itself.

The program is run in the example's working directory, inherits the environment unless overridden, and is killed after the configured timeout expires.

A timeout is treated as a fatal error and counted separately from normal mismatches.

### Global setup and cleanup

The global hooks are executed once per file, not once per example:

- `global-setup`: runs before the first example in the file
- `global-cleanup`: runs after the last example in the file

The per-example hooks keep their usual meaning:

- `setup`: runs before each example
- `cleanup`: runs after each example

### Output blocks

`cli-test-out` and `cli-test-err` accept either:

- inline text, or
- a path to a file containing the expected output.

When inline text is used, indentation rules applies, see [indentation.md](indentation.md)

When a file path is used, it is resolved relative to the source file containing the example. The file content is read as bytes and used as the expected output.

When `hexdump=1`, the expected output is interpreted as a hex dump rather than literal text. The hex dump is converted to the equivalent bytes before comparison.

### Comparison semantics

By default, comparison is byte-for-byte and exact.

If a custom comparison function is supplied via `cmp`, it must be named `compare` and accept exactly two positional arguments: `expected` and `actual`. Both values are bytes. The function must return a boolean value indicating whether the outputs match.

### Failure reporting

After executing all examples of a file, `cli-test` reports:

- the absolute path of the file
- how many examples were found
- how many passed
- how many timed out
- how many failed
- for each failure, a detailed diagnostic including:
  - the example index and file location (line number and column of the first mismatch byte position)
  - whether the mismatch was on `stdout` or `stderr`
  - the first mismatching byte position and both expected/actual byte values
  - the full actual output

The first differing byte is reported. If one output is shorter than the other, the mismatch is reported at the first missing byte.

### Temporary directories and reuse

By default, each example runs in a separate temporary directory. The example is independent from others. If `reuse=1`, all examples in the same file share the same working directory and environment state.

If `seq=1`, examples run sequentially. If `seq=0`, they may run concurrently.

