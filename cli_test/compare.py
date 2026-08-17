from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Callable


def default_compare(expected: bytes, actual: bytes) -> bool:
    return expected == actual


def load_compare(path: str) -> Callable[[bytes, bytes], bool]:
    module_path = Path(path)
    spec = importlib.util.spec_from_file_location("cli_test_compare", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load comparison module: {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    compare = getattr(module, "compare", None)
    if compare is None:
        raise ValueError(f"Comparison module {path!r} does not define compare(expected, actual)")
    return compare
