"""The package must not grow a browser driver or an invite POST."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "lin"
BANNED = ("playwright", "9222", "voyager", "normInvitation", "USER_LINKEDIN", "PW_LINKEDIN")


def test_package_has_no_browser_or_invite_post() -> None:
    for path in PKG.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in BANNED:
            assert token not in text, f"{path.name} contains {token}"


def test_prepare_does_not_import_http() -> None:
    tree = ast.parse((PKG / "policy" / "prepare.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("lin.http")
