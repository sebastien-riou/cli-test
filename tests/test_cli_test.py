from pathlib import Path

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
