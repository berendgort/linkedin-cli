"""Pick one person. Two matches return candidates."""

from __future__ import annotations

from lin.core.exceptions import LinAmbiguousError, LinNotFoundError
from lin.models.lead import Lead

__all__ = ("resolve_leads",)

_LIMIT = 8


def resolve_leads(query: str, leads: list[Lead]) -> Lead:
    if not leads:
        raise LinNotFoundError(f"No person for {query!r}")
    by_slug = [lead for lead in leads if lead.slug == query]
    if len(by_slug) == 1:
        return by_slug[0]
    needle = query.casefold()
    by_name = [lead for lead in leads if lead.name.casefold() == needle]
    if len(by_name) == 1:
        return by_name[0]
    if len(leads) == 1 and not by_name:
        return leads[0]
    shown = by_name or leads
    raise LinAmbiguousError(
        f"{len(shown)} people match {query!r}. Pass a slug.",
        candidates=shown[:_LIMIT],
    )
