"""Lead, score, invite row, and the draft handed to a human."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

__all__ = ("Budget", "Draft", "Invite", "InviteStatus", "Lead", "Score")

InviteStatus = Literal["invited", "accepted", "withdrawn"]


class Lead(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    name: str
    title: str
    country: str
    connections: int
    has_photo: bool
    text: str


class Score(BaseModel):
    model_config = ConfigDict(frozen=True)

    passed: bool
    reasons: tuple[str, ...]


class Invite(BaseModel):
    model_config = ConfigDict(frozen=True)

    day: date
    slug: str
    status: InviteStatus


class Budget(BaseModel):
    model_config = ConfigDict(frozen=True)

    day: date
    rest: bool
    target: int
    hard_cap: int
    today: int
    week: int
    remaining: int
    gate: str


class Draft(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    name: str
    note: str
    chars: int
    version: str
    url: str
    stopped_before_send: bool = True
    remaining: int
