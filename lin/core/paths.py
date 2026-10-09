"""Config directory. Session file is mode 0600. No network."""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ("invites_path", "lin_home", "profile_path", "session_path")


def lin_home() -> Path:
    override = os.environ.get("LIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".config" / "lin"


def profile_path() -> Path:
    return lin_home() / "profile.json"


def session_path() -> Path:
    return lin_home() / "session.json"


def invites_path() -> Path:
    return lin_home() / "invites.jsonl"
