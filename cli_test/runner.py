from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict


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

    return {
        "ok": True,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }
