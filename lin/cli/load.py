"""Load a local JSON fixture. No network."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lin.core.exceptions import LinValidationError

__all__ = ("load_json",)


def load_json(path: str) -> Any:
    file = Path(path)
    if not file.is_file():
        raise LinValidationError(f"fixture not found: {path}")
    return json.loads(file.read_text(encoding="utf-8"))
