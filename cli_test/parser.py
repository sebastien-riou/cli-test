from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


MARKERS = (
    "cli-test-cmd",
    "cli-test-cfg",
    "cli-test-out",
    "cli-test-err",
    "cli-test-end",
)


@dataclass
class Example:
    cmd: str = ""
    stdout: str = ""
    stderr: str = ""
    config: Dict[str, object] = field(default_factory=dict)
    path: Optional[Path] = None
    index: int = 0


def _match_marker(line: str) -> Optional[Tuple[str, str]]:
    for marker in MARKERS:
        pos = line.find(marker)
        if pos < 0:
            continue
        suffix = line[pos + len(marker) :]
        if suffix.strip() == "":
            return line[:pos], marker
    return None


def _strip_block_prefix(line: str, block_prefix: str) -> str:
    if block_prefix and line.startswith(block_prefix):
        return line[len(block_prefix) :]
    return line


def _leading_ws(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def _compute_content_indent(lines: List[str], block_prefix: str) -> str:
    for line in lines:
        if not line.strip():
            continue
        without_block = _strip_block_prefix(line, block_prefix)
        return without_block[: len(without_block) - len(without_block.lstrip())]
    return ""


def _normalize_block(lines: List[str], block_prefix: str, content_indent: str) -> str:
    out: List[str] = []
    for line in lines:
        if not line.strip():
            out.append("")
            continue
        without_block = _strip_block_prefix(line, block_prefix)
        if content_indent and without_block.startswith(content_indent):
            without_block = without_block[len(content_indent) :]
        out.append(without_block)
    return "\n".join(out)


def _parse_cfg_block(lines: List[str]) -> Dict[str, object]:
    cfg: Dict[str, object] = {}
    for raw in lines:
        text = raw.strip()
        if not text:
            continue
        if "=" not in text:
            raise ValueError(f"Invalid config line: {raw!r}")
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid config key in: {raw!r}")
        cfg[key] = value
    return cfg


def parse_file(path: Path | str) -> List[Example]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    examples: List[Example] = []
    current: Optional[Example] = None
    current_section: Optional[str] = None
    sections: Dict[str, List[str]] = {}
    block_prefix = ""
    content_indent = ""

    for line in lines:
        match = _match_marker(line)
        if match is not None:
            prefix, marker = match
            if marker == "cli-test-cmd":
                current = Example(path=file_path, index=len(examples) + 1)
                current_section = "cmd"
                sections = {"cmd": []}
                block_prefix = prefix
                content_indent = ""
                continue

            if current is None:
                continue

            if marker == "cli-test-cfg":
                current_section = "cfg"
                sections.setdefault("cfg", [])
                continue

            if marker == "cli-test-out":
                current_section = "stdout"
                sections.setdefault("stdout", [])
                continue

            if marker == "cli-test-err":
                current_section = "stderr"
                sections.setdefault("stderr", [])
                continue

            if marker == "cli-test-end":
                if current is not None:
                    content_indent = _compute_content_indent(sections.get("cmd", []), block_prefix)
                    current.cmd = _normalize_block(sections.get("cmd", []), block_prefix, content_indent)
                    current.config = _parse_cfg_block(sections.get("cfg", []))
                    current.stdout = _normalize_block(sections.get("stdout", []), block_prefix, content_indent)
                    current.stderr = _normalize_block(sections.get("stderr", []), block_prefix, content_indent)
                    examples.append(current)
                current = None
                current_section = None
                sections = {}
                block_prefix = ""
                content_indent = ""
                continue

        if current is not None and current_section is not None:
            sections.setdefault(current_section, []).append(line)

    if current is not None:
        content_indent = _compute_content_indent(sections.get("cmd", []), block_prefix)
        current.cmd = _normalize_block(sections.get("cmd", []), block_prefix, content_indent)
        current.config = _parse_cfg_block(sections.get("cfg", []))
        current.stdout = _normalize_block(sections.get("stdout", []), block_prefix, content_indent)
        current.stderr = _normalize_block(sections.get("stderr", []), block_prefix, content_indent)
        examples.append(current)

    return examples
