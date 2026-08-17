from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass
class Config:
    timeout: int = 30
    run_dir: Optional[str] = None
    path: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    setup: Optional[str] = None
    global_setup: Optional[str] = None
    cleanup: Optional[str] = None
    global_cleanup: Optional[str] = None
    cmp: Optional[str] = None
    seq: int = 0
    reuse: int = 0
    prefix: str = "cli-test-"
    hexdump: int = 0

    def apply_override(self, overrides: Dict[str, object]) -> "Config":
        merged = Config(**self.__dict__)
        for key, value in overrides.items():
            if key not in merged.__dict__:
                raise ValueError(f"Unknown config key: {key}")
            if key in {"timeout", "seq", "reuse", "hexdump"}:
                setattr(merged, key, _coerce_int(value))
            elif key == "path":
                setattr(merged, key, _coerce_path_list(value))
            elif key == "env":
                setattr(merged, key, _coerce_env(value))
            elif key in {"run_dir", "setup", "global_setup", "cleanup", "global_cleanup", "cmp", "prefix"}:
                setattr(merged, key, value)
            else:
                setattr(merged, key, value)
        return merged


def _coerce_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0
        if text.lower() in {"0", "1"}:
            return int(text)
        return parse_duration(text)
    raise TypeError(f"Expected int-like value, got {value!r}")


def parse_duration(text: str) -> int:
    text = text.strip()
    if not text:
        return 0

    suffix_map = {
        "ms": 0.001,
        "s": 1.0,
        "m": 60.0,
        "h": 3600.0,
    }
    for suffix, factor in suffix_map.items():
        if text.lower().endswith(suffix):
            number = text[: -len(suffix)]
            return int(float(number) * factor)
    return int(float(text))


def _coerce_path_list(value: object) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part for part in value.split(os.pathsep) if part]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return [str(value)]


def _coerce_env(value: object) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not value:
        return env
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    if isinstance(value, str):
        for item in value.split(os.pathsep):
            if not item:
                continue
            if "=" not in item:
                raise ValueError(f"Invalid env entry: {item!r}")
            key, val = item.split("=", 1)
            env[key] = val
        return env
    for item in value:
        if "=" not in str(item):
            raise ValueError(f"Invalid env entry: {item!r}")
        key, val = str(item).split("=", 1)
        env[key] = val
    return env


def merge_config(base: Config, override: Dict[str, object]) -> Config:
    return base.apply_override(override)


def default_config() -> Config:
    return Config()
