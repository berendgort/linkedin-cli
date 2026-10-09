"""ICP bar. A lead passes or it does not. No silent maybe."""

from __future__ import annotations

from lin.models.lead import Lead, Score

__all__ = ("score_lead",)

_TITLES = ("medical director", "supervising physician")
_WEIGHT = (
    "glp-1",
    "glp1",
    "weight loss",
    "weight-loss",
    "obesity",
    "semaglutide",
    "tirzepatide",
    "wegovy",
    "mounjaro",
    "ozempic",
)
_HARD_BAN = (
    "hospital",
    "academic",
    "pharma",
    "biotech",
    "insurer",
    "insurance",
    "fertility",
    "behavioral health",
    "one medical",
)
_MEDSPA = ("medspa", "med spa", "aesthetics")
_US = {"us", "usa", "united states"}


def _has(blob: str, words: tuple[str, ...]) -> bool:
    return any(word in blob for word in words)


def score_lead(lead: Lead) -> Score:
    reasons: list[str] = []
    title = lead.title.casefold()
    blob = f"{title}\n{lead.text.casefold()}"
    if not any(role in title for role in _TITLES):
        reasons.append("title is not medical director or supervising physician")
    if lead.country.casefold() not in _US:
        reasons.append("not US-based")
    if lead.connections < 100:
        reasons.append("fewer than 100 connections")
    if not lead.has_photo:
        reasons.append("no profile photo")
    if _has(blob, _HARD_BAN):
        reasons.append("hospital, pharma, insurer, fertility, or similar disqualifier")
    weight = _has(blob, _WEIGHT)
    if _has(blob, _MEDSPA) and not weight:
        reasons.append("medspa or aesthetics without a weight-loss signal")
    if not weight:
        reasons.append("no GLP-1 or medical weight-loss signal")
    return Score(passed=not reasons, reasons=tuple(reasons))
