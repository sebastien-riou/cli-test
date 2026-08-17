from __future__ import annotations

import shlex
import subprocess
from typing import Any, Dict


def _byte_location(data: bytes, offset: int) -> Dict[str, int]:
    if offset < 0:
        offset = 0
    line = 1
    column = 1
    for index in range(offset):
        if index >= len(data):
            break
        if data[index] == 10:
            line += 1
            column = 1
        else:
            column += 1
    return {"line": line, "column": column}


def _first_mismatch_index(expected: bytes, actual: bytes) -> int:
    limit = min(len(expected), len(actual))
    for i in range(limit):
        if expected[i] != actual[i]:
            return i
    if len(expected) != len(actual):
        return limit
    return -1


def run_example(command: str, cwd: str | None = None, timeout: int = 30, env: Dict[str, str] | None = None) -> Dict[str, Any]:
    argv = shlex.split(command)
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        capture_output=True,
        timeout=timeout,
        text=True,
    )

    stdout = completed.stdout.encode("utf-8") if isinstance(completed.stdout, str) else b""
    stderr = completed.stderr.encode("utf-8") if isinstance(completed.stderr, str) else b""
    mismatch = _first_mismatch_index(stdout, stdout)
    location = _byte_location(stdout, mismatch if mismatch >= 0 else 0)

    return {
        "ok": True,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
        "location": location,
        "mismatch_index": mismatch,
    }
