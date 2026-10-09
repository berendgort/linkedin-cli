"""Local profile and session. The store is the only writer."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ("Profile", "Session")


class Profile(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str = ""
    blocked: tuple[str, ...] = ()
    hard_cap: int = 15
    weekly_cap: int = 80
    force: bool = False


class Session(BaseModel):
    model_config = ConfigDict(frozen=True)

    cookie: str = Field(repr=False)
