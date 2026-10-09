"""Render the locked note. The only substitution is the name."""

from __future__ import annotations

from lin.core.exceptions import LinValidationError
from lin.policy.copy import NOTE_LIMIT, NOTE_V20, NOTE_V21

__all__ = ("greeting_name", "render_note")

_VERSIONS = {"v2": NOTE_V20, "v21": NOTE_V21}


def greeting_name(name: str) -> str:
    cleaned = " ".join(name.split())
    if not cleaned:
        raise LinValidationError("name is empty")
    folded = cleaned.casefold()
    if folded.startswith("dr.") or folded.startswith("dr "):
        return cleaned
    return f"Dr. {cleaned}"


def render_note(name: str, version: str = "v2") -> str:
    template = _VERSIONS.get(version)
    if template is None:
        raise LinValidationError("note version must be v2 or v21")
    note = template.replace("Dr. X", greeting_name(name))
    if "\u2014" in note or "\u2013" in note:
        raise LinValidationError("note contains a dash the template forbids")
    limit = NOTE_LIMIT[version]
    if len(note) > limit:
        raise LinValidationError(f"note is {len(note)} chars; limit is {limit}")
    return note
