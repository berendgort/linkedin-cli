"""Slug and day checks shared by the store and the draft."""

from __future__ import annotations

import re
from datetime import date

from lin.core.exceptions import LinValidationError

__all__ = ("check_slug", "parse_day")

_SLUG = re.compile(r"^[a-z0-9-]{3,80}$")


def check_slug(slug: str) -> str:
    if _SLUG.match(slug) is None:
        raise LinValidationError("slug must be 3-80 lowercase letters, digits, or hyphens")
    return slug


def parse_day(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise LinValidationError("day must be YYYY-MM-DD") from exc
