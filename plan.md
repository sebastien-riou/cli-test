# Minimal implementation plan for cli-test

This plan is based on the behavior described in [README.md](README.md) and the exact indentation semantics captured in [indentation.md](indentation.md).

## 1) Core data model

Create a small parser that turns a source file into a list of example objects:

- Example
  - index
  - file_path
  - cmd_text
  - stdout_text
  - stderr_text
  - config: dict
  - line numbers for reporting
  - raw blocks for diagnostics

Each example is built from marker blocks:

- `cli-test-cmd`
- `cli-test-cfg`
- `cli-test-out`
- `cli-test-err`
- `cli-test-end`

## 2) Parse file into examples

Implement a line-based scanner:

- iterate over lines in the file
- detect marker lines using the configured prefix, defaulting to `cli-test-`
- keep a current example state
- when a new marker appears, close the previous block and start a new one
- support both inline content and file-based expected output

Important rule from [indentation.md](indentation.md):

- `block level indentation` = everything before the marker text on the marker line
- `content level indentation` = leading whitespace on the first content line immediately after `cli-test-cmd`, after removing the block prefix

Example:

- `#    cli-test-cmd` => block prefix is `#    `
- next line `#        echo ' he'` => after removing `#    `, the content line becomes `        echo ' he'`
- content indent is 8 spaces, so the final command is `echo ' he'`

This is the exact rule the examples rely on.

## 3) Normalize text blocks using the two indentation levels

Add a helper function like:

- `strip_block_prefix(line, block_prefix)`
- `strip_content_prefix(line, content_indent)`

For any command or output block:

- remove the block-level prefix
- remove the content-level prefix from the left edge of each line
- preserve all other characters exactly, including remaining spaces

This matches the examples in [indentation.md](indentation.md), where:

- `    cli-test-cmd` becomes `cli-test-cmd`
- `        echo ' he'` becomes `echo ' he'`
- `         he` becomes ` he`

## 4) Parse per-example configuration

Implement a simple parser for `cli-test-cfg`:

- read one line per setting
- require `key=value`
- reject unknown keys and duplicate keys
- merge into the current example config
- apply config overrides before execution

Supported keys from [README.md](README.md):

- `timeout`
- `run-dir`
- `path`
- `env`
- `setup`
- `cleanup`
- `seq`
- `reuse`
- `hexdump`
- `cmp`

## 5) Resolve expected output

For `cli-test-out` / `cli-test-err`:

- if the value is a path, read that file relative to the current source file
- otherwise use the inline text after indentation normalization
- if `hexdump=1`, decode the hex dump to bytes before comparison

This should be a helper such as:

- `resolve_expected(value, source_path, hexdump) -> bytes`

## 6) Execute commands

Add a runner module:

- `run_example(example, global_cfg) -> Result`
- use `subprocess.run(..., shell=False)`
- tokenize command using `shlex.split` on POSIX / equivalent on Windows
- set `cwd` to `run-dir` or a temp dir
- inherit environment unless overridden
- capture stdout/stderr as bytes
- enforce the timeout value
- mark timeout as a distinct status

This matches the README’s execution rules.

## 7) Compare outputs

Default comparison:

- byte-for-byte equality

Custom comparison:

- if `cmp` is set, load the Python script and call `compare(expected, actual)`
- expect `compare(expected: bytes, actual: bytes) -> bool`

## 8) Report failures

Create a result object with states:

- pass
- fail
- timeout

On mismatch:

- report file path
- example index
- stream (`stdout` or `stderr`)
- byte offset
- expected byte and actual byte
- full actual output

This matches the reporting rules in [README.md](README.md).

## 9) File-level orchestration

Main flow:

1. scan files
2. parse examples
3. apply defaults
4. run each example
5. aggregate pass/fail/timeout counts
6. print summary
7. exit status:
   - `0` if all pass
   - `1` if any fail/timeout
   - `2` for invalid input/config

## 10) Minimal module layout

A minimal implementation could look like this:

- `cli_test/__init__.py`
- `cli_test/parser.py`
  - scan marker blocks
  - apply indentation normalization
- `cli_test/config.py`
  - parse `cli-test-cfg`
  - merge config
- `cli_test/runner.py`
  - execute command and capture output
- `cli_test/compare.py`
  - default and custom comparison
- `cli_test/cli.py`
  - argparse entry point

## 11) Minimal pseudocode

```python
def process_file(path, global_cfg):
    lines = read_lines(path)
    examples = parse_examples(lines, prefix=global_cfg.prefix)
    results = []

    for ex in examples:
        cfg = merge(global_cfg, ex.config)
        expected_out = resolve_expected(ex.stdout_text, path, cfg.hexdump)
        expected_err = resolve_expected(ex.stderr_text, path, cfg.hexdump)
        result = run_example(ex.cmd_text, cfg, expected_out, expected_err)
        results.append(result)

    return summarize(results)
```

This is the smallest implementation that matches both documents without guessing beyond the rules they describe.
