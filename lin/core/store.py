"""One writer for profile.json, session.json, and invites.jsonl."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from lin.core.exceptions import LinValidationError
from lin.core.paths import invites_path, lin_home, profile_path, session_path
from lin.models.lead import Invite
from lin.models.profile import Profile, Session

__all__ = (
    "append_invite",
    "load_invites",
    "load_profile",
    "load_session",
    "save_profile",
    "save_session",
)


def _ensure_home() -> None:
    home = lin_home()
    home.mkdir(parents=True, exist_ok=True)
    os.chmod(home, 0o700)


def _atomic_write(path: Path, text: str) -> None:
    """Write via a unique 0600 temp file, then replace the destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def load_profile() -> Profile | None:
    path = profile_path()
    if not path.is_file():
        return None
    return Profile.model_validate_json(path.read_text(encoding="utf-8"))


def save_profile(profile: Profile) -> None:
    _ensure_home()
    text = json.dumps(profile.model_dump(mode="json"), indent=2) + "\n"
    _atomic_write(profile_path(), text)


def load_session() -> Session | None:
    path = session_path()
    if not path.is_file():
        return None
    return Session.model_validate_json(path.read_text(encoding="utf-8"))


def save_session(session: Session) -> None:
    _ensure_home()
    payload = json.dumps({"cookie": session.cookie}) + "\n"
    _atomic_write(session_path(), payload)


def load_invites() -> tuple[Invite, ...]:
    path = invites_path()
    if not path.is_file():
        return ()
    rows: list[Invite] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(Invite.model_validate_json(line))
    return tuple(rows)


def append_invite(invite: Invite) -> tuple[Invite, ...]:
    """Idempotent on (day, slug). A second log does not add a second row."""
    if not invite.slug.strip():
        raise LinValidationError("slug is empty")
    _ensure_home()
    current = load_invites()
    for row in current:
        if row.day == invite.day and row.slug == invite.slug:
            return current
    nxt = current + (invite,)
    text = "".join(row.model_dump_json() + "\n" for row in nxt)
    _atomic_write(invites_path(), text)
    return nxt
