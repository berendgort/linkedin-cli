"""No live LinkedIn client. Send stays unsupported until a fixture exists."""

from __future__ import annotations

from typing import NoReturn

from lin.core.exceptions import LinUnsupportedError

__all__ = ("send_invite",)


def send_invite(slug: str, note: str) -> NoReturn:
    """Refuse. The invite POST has not been captured."""
    _ = (slug, note)
    raise LinUnsupportedError(
        "Invite send has no captured fixture. Open the prepare URL and send the note yourself."
    )
