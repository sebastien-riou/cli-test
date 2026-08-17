# Test Coverage Status

This document lists each feature documented in README.md and indicates whether it is tested.

## Markers

### `cli-test-cmd` marker
- **Status**: ✅ TESTED
- **Tests**: 
  - `test_parse_simple_example` (unit test)
  - `test_parse_comment_indented_example` (unit test)
  - `test_file_based_test_cases[simple_pass]` (file-based)
  - `test_file_based_test_cases[comment_indented]` (file-based)
  - `test_file_based_test_cases[stderr_with_empty_stdout]` (file-based)
  - `test_file_based_test_cases[stdout_mismatch]` (file-based)

### `cli-test-cfg` marker
- **Status**: ❌ NOT TESTED
- **Notes**: Configuration block parsing not covered in test cases

### `cli-test-out` marker for stdout
- **Status**: ✅ TESTED
- **Tests**:
  - `test_parse_simple_example` (unit test)
  - `test_parse_comment_indented_example` (unit test)
  - `test_file_based_test_cases[simple_pass]` (file-based)
  - `test_file_based_test_cases[comment_indented]` (file-based)
  - `test_file_based_test_cases[stdout_mismatch]` (file-based)

### `cli-test-err` marker for stderr
- **Status**: ✅ TESTED
- **Tests**:
  - `test_file_based_test_cases[stderr_with_empty_stdout]` (file-based)

### `cli-test-end` marker
- **Status**: ✅ TESTED
- **Tests**: All parser and file-based tests (marker is required for all examples)

## Default Behaviors

### Each example runs in a temporary directory
- **Status**: ❌ NOT TESTED
- **Notes**: Implementation exists but no test validates isolation

### Examples may run concurrently
- **Status**: ❌ NOT TESTED
- **Notes**: No test for concurrent execution behavior

### Environment variables inherited from cli-test
- **Status**: ❌ NOT TESTED
- **Notes**: No test validates environment inheritance

### Program runs with same user that invoked cli-test
- **Status**: ❌ NOT TESTED
- **Notes**: Not applicable to typical test scenarios

### Program runs within same python environment
- **Status**: ❌ NOT TESTED
- **Notes**: No test validates python environment

### 30s default timeout
- **Status**: ❌ NOT TESTED
- **Notes**: Timeout behavior not tested

## CLI Options

### `--run-dir`
- **Status**: ❌ NOT TESTED
- **Notes**: Working directory override not covered

### `--path`
- **Status**: ❌ NOT TESTED
- **Notes**: PATH environment extension not covered

### `--env`
- **Status**: ❌ NOT TESTED
- **Notes**: Environment variable override not covered

### `--timeout`
- **Status**: ❌ NOT TESTED
- **Notes**: Custom timeout not covered

### `--setup`
- **Status**: ❌ NOT TESTED
- **Notes**: Per-example setup hook not covered

### `--global-setup`
- **Status**: ❌ NOT TESTED
- **Notes**: Global setup hook not covered

### `--cleanup`
- **Status**: ❌ NOT TESTED
- **Notes**: Per-example cleanup hook not covered

### `--global-cleanup`
- **Status**: ❌ NOT TESTED
- **Notes**: Global cleanup hook not covered

### `--cmp`
- **Status**: ❌ NOT TESTED
- **Notes**: Custom comparison function not covered

### `--seq`
- **Status**: ❌ NOT TESTED
- **Notes**: Sequential execution mode not covered

### `--reuse`
- **Status**: ❌ NOT TESTED
- **Notes**: Reusable environment across examples not covered

### `--prefix`
- **Status**: ❌ NOT TESTED
- **Notes**: Custom marker prefix not covered

### `--hexdump`
- **Status**: ❌ NOT TESTED
- **Notes**: Hexadecimal dump format not covered

## Config Syntax

### Config key=value format
- **Status**: ❌ NOT TESTED
- **Notes**: `cli-test-cfg` block parsing not covered

### Duration strings (e.g., 10s, 2m, 500ms)
- **Status**: ❌ NOT TESTED
- **Notes**: Duration parsing not covered

### Per-example config overrides
- **Status**: ❌ NOT TESTED
- **Notes**: Config override mechanism not covered

## Command Execution

### Command parsing with shlex.split
- **Status**: ✅ PARTIALLY TESTED
- **Tests**:
  - `test_run_example_passes` (unit test)
  - Various file-based tests use quoted commands
- **Notes**: Basic command parsing works but edge cases not covered

### Execution with shell=False
- **Status**: ✅ TESTED (implicitly)
- **Tests**: `test_run_example_passes` demonstrates shell-less execution
- **Notes**: Tests show commands execute without shell interpretation

### Timeout handling and fatal error reporting
- **Status**: ❌ NOT TESTED
- **Notes**: Timeout is detected but not explicitly tested

## Output Blocks

### Inline text output
- **Status**: ✅ TESTED
- **Tests**:
  - `test_parse_simple_example` (unit test)
  - `test_file_based_test_cases[simple_pass]` (file-based)
  - `test_file_based_test_cases[stderr_with_empty_stdout]` (file-based)

### File path for expected output
- **Status**: ❌ NOT TESTED
- **Notes**: File references (e.g., `@filename`) not covered

### Indentation rules
- **Status**: ✅ TESTED
- **Tests**:
  - `test_parse_comment_indented_example` (unit test)
  - `test_file_based_test_cases[comment_indented]` (file-based)
- **Notes**: Comment indentation and content indentation tested

### Hexdump format
- **Status**: ✅ TESTED
- **Tests**: `test_file_based_test_cases[hexdump]` (file-based, 5 examples)
- **Notes**: Tests various hexdump formats including simple hex, offset headers, ASCII representation, and end offset markers

## Comparison Semantics

### Default byte-for-byte exact comparison
- **Status**: ✅ TESTED
- **Tests**:
  - `test_run_example_passes` (unit test)
  - `test_file_based_test_cases[simple_pass]` (file-based)
  - `test_file_based_test_cases[comment_indented]` (file-based)

### Custom comparison function (cmp)
- **Status**: ❌ NOT TESTED
- **Notes**: Custom comparison function loading and execution not covered

## Failure Reporting

### Absolute file path in report
- **Status**: ✅ TESTED
- **Tests**: `test_file_based_test_cases` tests check output format

### Example count reporting
- **Status**: ✅ TESTED
- **Tests**: All file-based tests verify example count in output

### Passed count
- **Status**: ✅ TESTED
- **Tests**:
  - `test_file_based_test_cases[simple_pass]`
  - `test_file_based_test_cases[comment_indented]`
  - `test_file_based_test_cases[stderr_with_empty_stdout]`

### Timeout count
- **Status**: ❌ NOT TESTED
- **Notes**: Timeout reporting not covered (timeout exit code is 1)

### Failed count
- **Status**: ✅ TESTED
- **Tests**: `test_file_based_test_cases[stdout_mismatch]`

### Mismatch location (line and column numbers)
- **Status**: ✅ TESTED
- **Tests**:
  - `test_run_example_reports_location_on_mismatch` (unit test)
  - `test_file_based_test_cases[stdout_mismatch]` (file-based)

### stdout vs stderr distinction in failure
- **Status**: ✅ TESTED
- **Tests**:
  - `test_file_based_test_cases[stderr_with_empty_stdout]`
  - `test_file_based_test_cases[stdout_mismatch]`

### First mismatch byte position
- **Status**: ✅ TESTED
- **Tests**: `test_file_based_test_cases[stdout_mismatch]` checks mismatch location

## Temporary Directories and Reuse

### Each example in separate temporary directory
- **Status**: ❌ NOT TESTED
- **Notes**: Default behavior implemented but not explicitly tested

### `reuse=1` for shared working directory
- **Status**: ❌ NOT TESTED
- **Notes**: Reuse option not covered

### `seq=1` for sequential execution
- **Status**: ❌ NOT TESTED
- **Notes**: Sequential mode not covered

---

## Summary

- **Total Features**: 41
- **Tested**: 16 (39.0%)
- **Partially Tested**: 2 (4.9%)
- **Not Tested**: 23 (56.1%)

### Key Gaps
1. **Configuration system**: `cli-test-cfg` block and most config options (timeout, run-dir, path, env, seq, reuse, prefix) not tested
2. **CLI options**: Most command-line arguments not tested
3. **Hooks**: Setup and cleanup hooks (both per-example and global) not tested
4. **Advanced features**: Custom comparison functions, file references for output
5. **Concurrency and isolation**: Sequential/concurrent execution, reuse not tested
6. **Environment control**: PATH, environment variables, working directory customization
