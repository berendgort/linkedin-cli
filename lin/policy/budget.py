"""Daily and weekly invite budget. The human's log is the only count."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from lin.models.lead import Budget, Invite

__all__ = ("plan_budget",)

_HARD_CAP = 15
_MATURE_DAYS = 14
_MIN_SAMPLE = 20


def _epoch_day(day: date) -> int:
    stamp = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return int(stamp.timestamp()) // 86400


def _soft_target(day: date) -> int:
    return 8 + (_epoch_day(day) * 17) % 5


def _rest(day: date) -> bool:
    return _epoch_day(day) % 7 in (0, 4)


def _counts(day: date, invites: tuple[Invite, ...] | list[Invite]) -> tuple[int, int, int, int]:
    today = 0
    week = 0
    matured = 0
    accepted = 0
    cut = day - timedelta(days=_MATURE_DAYS)
    for row in invites:
        if row.status == "withdrawn":
            continue
        age = (day - row.day).days
        if row.day == day:
            today += 1
        if 0 <= age <= 6:
            week += 1
        if row.status == "accepted":
            accepted += 1
            matured += 1
        elif row.status == "invited" and row.day <= cut:
            matured += 1
    return today, week, matured, accepted


def plan_budget(
    day: date,
    invites: tuple[Invite, ...] | list[Invite],
    *,
    hard_cap: int = _HARD_CAP,
    weekly_cap: int = 80,
    force: bool = False,
) -> Budget:
    rest = _rest(day) and not force
    target = _soft_target(day)
    gate = "ok"
    today, week, matured, accepted = _counts(day, invites)
    if matured >= _MIN_SAMPLE and matured > 0:
        rate = accepted / matured
        if rate < 0.10 and not force:
            rest = True
            target = 0
            gate = "pause"
        elif rate < 0.25:
            target = min(target, 5)
            gate = "throttle"
    if rest and gate != "pause":
        gate = "rest"
        target = 0
    ceiling = min(target, hard_cap, _HARD_CAP)
    remaining = max(0, min(ceiling - today, weekly_cap - week))
    if rest:
        remaining = 0
    return Budget(
        day=day,
        rest=rest,
        target=target,
        hard_cap=min(hard_cap, _HARD_CAP),
        today=today,
        week=week,
        remaining=remaining,
        gate=gate,
    )
