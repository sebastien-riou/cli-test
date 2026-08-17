from pathlib import Path

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


def test_cli_reports_absolute_file_location(tmp_path, capsys):
    path = tmp_path / "sample.txt"
    path.write_text(
        """cli-test-cmd
python -c \"import sys; sys.stdout.write('bye')\"
cli-test-out
bzz
cli-test-end
""",
        encoding="utf-8",
    )

    exit_code = main([str(path)])
    captured = capsys.readouterr().out

    assert exit_code == 1
    assert "mismatch at line 4, column 2" in captured
