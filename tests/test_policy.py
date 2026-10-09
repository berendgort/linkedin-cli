"""Note, ICP, budget, and the stop-before-send draft."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from lin.core.exceptions import LinAmbiguousError, LinUnsupportedError, LinValidationError
from lin.http.client import send_invite
from lin.models.lead import Invite, Lead
from lin.policy.budget import plan_budget
from lin.policy.copy import NOTE_V20
from lin.policy.icp import score_lead
from lin.policy.note import render_note
from lin.policy.prepare import prepare_draft
from lin.policy.resolve import resolve_leads

FIX = Path(__file__).resolve().parents[1] / "fixtures"


def _lead(name: str) -> Lead:
    payload = json.loads((FIX / name).read_text(encoding="utf-8"))
    return Lead.model_validate(payload)


def _open_day() -> date:
    day = date(2026, 1, 1)
    while plan_budget(day, ()).rest:
        day += timedelta(days=1)
    return day


def test_note_replaces_only_the_name() -> None:
    note = render_note("Ada North")
    assert note.startswith("Hi Dr. Ada North - ")
    assert "Dr. X" not in note
    assert len(note) <= 300
    assert NOTE_V20.startswith("Hi Dr. X - ")
    short = render_note("Ada North", "v21")
    assert len(short) <= 200


def test_long_name_fails_closed() -> None:
    with pytest.raises(LinValidationError):
        render_note("A" * 280)


def test_pass_and_medspa() -> None:
    assert score_lead(_lead("lead_pass.json")).passed
    missed = score_lead(_lead("lead_medspa.json"))
    assert missed.passed is False
    assert any("medspa" in reason for reason in missed.reasons)


def test_rest_days_and_soft_target() -> None:
    start = date(2026, 1, 1)
    rests = 0
    for offset in range(7):
        report = plan_budget(start + timedelta(days=offset), ())
        rests += int(report.rest)
        if not report.rest:
            assert 8 <= report.target <= 12
            assert report.remaining == report.target
    assert rests == 2


def test_caps_pause_and_throttle() -> None:
    day = _open_day()
    full = tuple(Invite(day=day, slug=f"s{i}", status="invited") for i in range(15))
    capped = plan_budget(day, full)
    assert capped.remaining == 0
    old = day - timedelta(days=30)
    paused_rows = tuple(Invite(day=old, slug=f"p{i}", status="invited") for i in range(20))
    paused = plan_budget(day, paused_rows)
    assert paused.gate == "pause"
    assert paused.remaining == 0
    mixed = tuple(
        Invite(day=old, slug=f"a{i}", status="accepted") for i in range(4)
    ) + tuple(Invite(day=old, slug=f"b{i}", status="invited") for i in range(16))
    throttled = plan_budget(day, mixed)
    assert throttled.gate == "throttle"
    assert throttled.target <= 5


def test_prepare_stops_and_blocks() -> None:
    day = _open_day()
    draft, budget = prepare_draft(
        slug="ada-north",
        name="Ada North",
        day=day,
        invites=(),
        lead=_lead("lead_pass.json"),
    )
    assert draft.stopped_before_send is True
    assert "ada-north" in draft.url
    assert budget.remaining > 0
    with pytest.raises(LinValidationError):
        prepare_draft(
            slug="ada-north",
            name="Ada North",
            day=day,
            invites=(),
            blocked=("ada-north",),
        )
    with pytest.raises(LinValidationError):
        prepare_draft(
            slug="ada-north",
            name="Ada North",
            day=day,
            invites=(),
            page_text="We want to confirm it's you",
        )


def test_ambiguous_name() -> None:
    rows = json.loads((FIX / "bench_two.json").read_text(encoding="utf-8"))
    leads = [Lead.model_validate(row) for row in rows]
    with pytest.raises(LinAmbiguousError) as caught:
        resolve_leads("Ada North", leads)
    assert len(caught.value.candidates) == 2
    assert resolve_leads("ada-north", leads).slug == "ada-north"


def test_send_is_unsupported() -> None:
    with pytest.raises(LinUnsupportedError):
        send_invite("ada-north", "note")
