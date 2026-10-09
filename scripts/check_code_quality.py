#!/usr/bin/env python3
"""Korotkevich checks for lin, plus a ban on uncaptured LinkedIn wire."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "lin"
MAX_LOC = 250

LAYER: dict[str, int] = {
    "lin.models": 10,
    "lin.core.exceptions": 15,
    "lin.http": 20,
    "lin.core": 30,
    "lin.policy": 40,
    "lin.cli": 50,
    "lin.mcp": 50,
}

PRINT_ALLOW = {"lin/cli/catch.py"}
BANNED = ("voyager", "normInvitation", "playwright", "9222")


def _pkg_rank(mod: str) -> int | None:
    for prefix, rank in sorted(LAYER.items(), key=lambda item: -len(item[0])):
        if mod == prefix or mod.startswith(prefix + "."):
            return rank
    return None


def check_loc() -> list[str]:
    bad: list[str] = []
    for path in PKG.rglob("*.py"):
        n = len(path.read_text(encoding="utf-8").splitlines())
        if n > MAX_LOC:
            bad.append(f"{path.relative_to(ROOT)}: {n} LOC > {MAX_LOC}")
    return bad


def check_emdash() -> list[str]:
    bad: list[str] = []
    for path in PKG.rglob("*.py"):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "\u2014" in line or "\u2013" in line:
                bad.append(f"{path.relative_to(ROOT)}:{i}: em/en-dash")
    return bad


def check_print() -> list[str]:
    bad: list[str] = []
    for path in PKG.rglob("*.py"):
        rel = str(path.relative_to(ROOT))
        if rel in PRINT_ALLOW:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "print":
                    bad.append(f"{rel}:{node.lineno}: bare print()")
    return bad


def check_layers() -> list[str]:
    bad: list[str] = []
    for path in PKG.rglob("*.py"):
        parts = path.relative_to(PKG).with_suffix("").parts
        if path.name == "__init__.py":
            mod = ".".join(("lin", *parts[:-1])) if len(parts) > 1 else "lin"
        else:
            mod = ".".join(("lin", *parts))
        src_rank = _pkg_rank(mod)
        if src_rank is None:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if not name.startswith("lin."):
                    continue
                dst = _pkg_rank(name)
                if dst is not None and dst > src_rank:
                    bad.append(
                        f"{path.relative_to(ROOT)}: {mod} (rank {src_rank}) "
                        f"imports higher {name} (rank {dst})"
                    )
    return bad


def check_no_wire() -> list[str]:
    bad: list[str] = []
    catalog = json.loads((ROOT / "fixtures" / "wire_contracts.json").read_text(encoding="utf-8"))
    if catalog.get("calls"):
        bad.append("wire catalog calls must stay empty until a fixture is captured")
    for path in PKG.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in BANNED:
            if token in text:
                bad.append(f"{path.relative_to(ROOT)} contains {token}")
    return bad


def main() -> int:
    bad = check_loc() + check_emdash() + check_print() + check_layers() + check_no_wire()
    if bad:
        print("\n".join(bad), file=sys.stderr)
        return 1
    print("code quality ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
