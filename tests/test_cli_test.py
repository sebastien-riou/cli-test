from pathlib import Path

import pytest

from cli_test.cli import main
from cli_test.parser import parse_file
from cli_test.runner import run_example


def test_parse_simple_example(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text(
        """cli-test-cmd
echo ' he'
cli-test-out
 he
cli-test-end
""",
        encoding="utf-8",
    )

    examples = parse_file(path)

    assert len(examples) == 1
    assert examples[0].cmd == "echo ' he'"
    assert examples[0].stdout == " he"
    assert examples[0].stderr == ""


def test_parse_comment_indented_example(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text(
        """#    cli-test-cmd
#        echo ' he'
#    cli-test-out
#         he
#    cli-test-end
""",
        encoding="utf-8",
    )

    examples = parse_file(path)

    assert len(examples) == 1
    assert examples[0].cmd == "echo ' he'"
    assert examples[0].stdout == " he"


def test_run_example_passes(tmp_path):
    cmd = "python -c \"import sys; sys.stdout.write(' he')\""
    result = run_example(cmd, cwd=str(tmp_path), timeout=5)

    assert result["ok"] is True
    assert result["stdout"] == " he"
    assert result["stderr"] == ""


def test_run_example_reports_location_on_mismatch(tmp_path):
    cmd = "python -c \"import sys; sys.stdout.write('bye')\""
    result = run_example(cmd, cwd=str(tmp_path), timeout=5)
    # expected output is the default ' he' in the runner call path when comparing a value
    # this asserts the mismatch metadata is present for the first differing byte.
    assert "location" in result
    assert result["location"]["line"] >= 1
    assert result["location"]["column"] >= 1


def _get_file_based_test_cases():
    """Discover all test cases from inputs/outputs directories."""
    inputs_dir = Path(__file__).parent / "inputs"
    outputs_dir = Path(__file__).parent / "outputs"
    
    if not inputs_dir.exists():
        return []
    
    test_cases = []
    for input_file in sorted(inputs_dir.glob("*.txt")):
        output_file = outputs_dir / input_file.name
        if output_file.exists():
            test_cases.append(pytest.param(
                input_file.stem,
                input_file,
                output_file,
                id=input_file.stem
            ))
    
    return test_cases


@pytest.mark.parametrize("test_name,input_file,output_file", _get_file_based_test_cases())
def test_file_based_test_cases(tmp_path, capsys, test_name, input_file, output_file):
    """Generic test function that runs CLI tests from input/output file pairs."""
    # Copy input file to temp directory with normalized name for output matching
    test_input = tmp_path / input_file.name
    test_input.write_text(input_file.read_text(encoding="utf-8"), encoding="utf-8")
    
    # Run the CLI
    exit_code = main([str(test_input)])
    captured = capsys.readouterr().out
    
    # Load expected output
    expected_output = output_file.read_text(encoding="utf-8")
    
    # Check that all expected lines are in the output
    # (We match line-by-line to be flexible with file paths)
    for expected_line in expected_output.strip().split("\n"):
        assert expected_line in captured, f"Expected line not found in output:\n  Expected: {expected_line}\n  Got: {captured}"
