"""Stop strings and the draft that is handed to a human. No HTTP."""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import quote

from lin.core.exceptions import LinValidationError
from lin.models.lead import Budget, Draft, Invite, Lead
from lin.policy.budget import plan_budget
from lin.policy.icp import score_lead
from lin.policy.note import render_note

__all__ = ("INVITE_URL", "prepare_draft", "restriction_hit")

INVITE_URL = "https://www.linkedin.com/preload/custom-invite/?vanityName={slug}"

_SLUG = re.compile(r"^[a-z0-9-]{3,80}$")
_STOP = (
    "unusual activity",
    "temporarily restricted",
    "confirm it's you",
    "security verification",
    "/checkpoint/",
)


def restriction_hit(text: str) -> str | None:
    folded = text.casefold()
    for item in _STOP:
        if item in folded:
            return item
    return None


def prepare_draft(
    *,
    slug: str,
    name: str,
    day: date,
    invites: tuple[Invite, ...] | list[Invite],
    blocked: tuple[str, ...] = (),
    lead: Lead | None = None,
    page_text: str = "",
    version: str = "v2",
    hard_cap: int = 15,
    weekly_cap: int = 80,
    force: bool = False,
) -> tuple[Draft, Budget]:
    if _SLUG.match(slug) is None:
        raise LinValidationError("slug must be 3-80 lowercase letters, digits, or hyphens")
    if slug in blocked:
        raise LinValidationError(f"{slug} is on the do-not-contact list")
    hit = restriction_hit(page_text)
    if hit is not None:
        raise LinValidationError(f"stop: LinkedIn showed {hit}")
    if lead is not None:
        scored = score_lead(lead)
        if not scored.passed:
            raise LinValidationError("; ".join(scored.reasons))
    budget = plan_budget(
        day, invites, hard_cap=hard_cap, weekly_cap=weekly_cap, force=force
    )
    if budget.remaining <= 0:
        raise LinValidationError(f"no invites left ({budget.gate})")
    note = render_note(name, version)
    url = INVITE_URL.format(slug=quote(slug, safe=""))
    draft = Draft(
        slug=slug,
        name=name,
        note=note,
        chars=len(note),
        version=version,
        url=url,
        stopped_before_send=True,
        remaining=budget.remaining,
    )
    return draft, budget
