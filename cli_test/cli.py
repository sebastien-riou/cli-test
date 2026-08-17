from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .compare import default_compare, load_compare
from .config import Config, default_config, merge_config
from .parser import parse_file


def _collect_files(paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file():
                    files.append(child)
        elif p.exists():
            files.append(p)
    return files


def _run_setup(cmd: Optional[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> None:
    if not cmd:
        return
    subprocess.run(shlex.split(cmd), cwd=cwd, env=env, check=False)


def _resolve_expected(raw: str, source_path: Path, hexdump: int) -> bytes:
    if not raw:
        return b""
    if raw.startswith("@"):
        file_path = (source_path.parent / raw[1:]).resolve()
        return file_path.read_bytes()
    value = raw.encode("utf-8")
    if hexdump:
        cleaned = "".join(ch for ch in raw if ch not in " \t\r\n")
        return bytes.fromhex(cleaned)
    return value


def _first_mismatch(expected: bytes, actual: bytes) -> int:
    limit = min(len(expected), len(actual))
    for offset in range(limit):
        if expected[offset] != actual[offset]:
            return offset
    if len(expected) != len(actual):
        return limit
    return -1


def _byte_position(data: bytes, offset: int, start_line: int = 1, start_column: int = 1) -> Dict[str, int]:
    if offset < 0:
        offset = 0
    line = start_line
    column = start_column
    for index in range(offset):
        if index >= len(data):
            break
        if data[index] == 10:
            line += 1
            column = 1
        else:
            column += 1
    return {"line": line, "column": column}


def run_example(example, cfg: Config) -> Dict[str, Any]:
    cwd = cfg.run_dir or os.getcwd()
    env = os.environ.copy()
    env.update(cfg.env)

    if cfg.path:
        env["PATH"] = os.pathsep.join(cfg.path + [env.get("PATH", "")]) if env.get("PATH") else os.pathsep.join(cfg.path)

    _run_setup(cfg.setup, cwd=cwd, env=env)

    try:
        result = subprocess.run(
            shlex.split(example.cmd),
            cwd=cwd,
            env=env,
            capture_output=True,
            timeout=cfg.timeout,
            text=False,
        )
        stdout = result.stdout
        stderr = result.stderr
        ok = True
        failed = None

        if cfg.hexdump:
            expected_stdout = _resolve_expected(example.stdout, example.path, 1)
            expected_stderr = _resolve_expected(example.stderr, example.path, 1)
        else:
            expected_stdout = _resolve_expected(example.stdout, example.path, 0)
            expected_stderr = _resolve_expected(example.stderr, example.path, 0)

        compare_fn = default_compare
        if cfg.cmp:
            compare_fn = load_compare(cfg.cmp)

        if example.stdout and not compare_fn(expected_stdout, stdout):
            ok = False
            offset = _first_mismatch(expected_stdout, stdout)
            start_line = example.stdout_start_line or 1
            failed = ("stdout", expected_stdout, stdout, _byte_position(expected_stdout, offset if offset >= 0 else 0, start_line=start_line))
        if example.stderr and not compare_fn(expected_stderr, stderr):
            ok = False
            offset = _first_mismatch(expected_stderr, stderr)
            start_line = example.stderr_start_line or 1
            failed = ("stderr", expected_stderr, stderr, _byte_position(expected_stderr, offset if offset >= 0 else 0, start_line=start_line))
        return {
            "ok": ok,
            "stdout": stdout,
            "stderr": stderr,
            "failed": failed,
            "returncode": result.returncode,
            "example": example,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "stdout": b"",
            "stderr": b"",
            "failed": ("timeout", b"", b"", {"line": 1, "column": 1}),
            "timeout": True,
            "example": example,
        }
    finally:
        _run_setup(cfg.cleanup, cwd=cwd, env=env)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="cli-test")
    parser.add_argument("paths", nargs="+", help="files or directories to scan")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--run-dir")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("--seq", type=int, default=0)
    parser.add_argument("--reuse", type=int, default=0)
    parser.add_argument("--prefix", default="cli-test-")
    parser.add_argument("--hexdump", type=int, default=0)
    parser.add_argument("--setup")
    parser.add_argument("--cleanup")
    parser.add_argument("--global-setup")
    parser.add_argument("--global-cleanup")
    parser.add_argument("--cmp")
    args = parser.parse_args(argv)

    base_cfg = default_config()
    base_cfg.timeout = args.timeout
    base_cfg.run_dir = args.run_dir
    base_cfg.path = args.path
    base_cfg.seq = args.seq
    base_cfg.reuse = args.reuse
    base_cfg.prefix = args.prefix
    base_cfg.hexdump = args.hexdump
    base_cfg.setup = args.setup
    base_cfg.cleanup = args.cleanup
    base_cfg.global_setup = args.global_setup
    base_cfg.global_cleanup = args.global_cleanup
    base_cfg.cmp = args.cmp

    for item in args.env:
        if "=" not in item:
            raise ValueError(f"Invalid --env value: {item!r}")
        key, value = item.split("=", 1)
        base_cfg.env[key] = value

    files = _collect_files(args.paths)
    total_examples = 0
    passed = 0
    timed_out = 0
    failed = 0

    for path in files:
        examples = parse_file(path)
        for example in examples:
            total_examples += 1
            cfg = merge_config(base_cfg, example.config)
            result = run_example(example, cfg)
            if result["ok"]:
                passed += 1
            elif result.get("timeout"):
                timed_out += 1
            else:
                failed += 1
                stream, expected, actual, location = result["failed"]
                print(f"FAIL: {path} example {example.index} {stream}")
                print(f"  mismatch at line {location['line']}, column {location['column']}")
                print(f"  expected: {expected!r}")
                print(f"  actual:   {actual!r}")

    print(f"{len(files)} files, {total_examples} examples, {passed} passed, {timed_out} timeout, {failed} failed")
    return 0 if failed == 0 and timed_out == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
