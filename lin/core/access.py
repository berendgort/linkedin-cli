"""Load profile and session or fail closed. No HTTP."""

from __future__ import annotations

from lin.core.exceptions import LinAuthError
from lin.core.store import load_profile, load_session
from lin.models.profile import Profile, Session

__all__ = ("require_profile", "require_session")


def require_profile() -> Profile:
    return load_profile() or Profile()


def require_session() -> Session:
    session = load_session()
    if session is None or not session.cookie:
        raise LinAuthError("No session saved")
    return session
