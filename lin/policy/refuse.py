"""Refuse follow-ups. They stay off."""

from __future__ import annotations

from lin.core.exceptions import LinValidationError

__all__ = ("refuse_inmail", "refuse_reply")


def refuse_reply() -> None:
    raise LinValidationError("Post-accept messages are off. Log the reply and stop.")


def refuse_inmail() -> None:
    raise LinValidationError("InMail is off. Do not spend credits from this CLI.")
