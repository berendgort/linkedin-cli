"""FastMCP tools. Does not import the CLI package."""

from __future__ import annotations

from typing import Any

from lin.core.envelope import error_payload, success_payload
from lin.core.exceptions import LinValidationError
from lin.core.instruct import instruct_recipe
from lin.core.slug import parse_day
from lin.core.store import load_invites, load_profile
from lin.models.profile import Profile
from lin.policy.note import render_note
from lin.policy.prepare import prepare_draft
from lin.policy.refuse import refuse_reply

__all__ = ("build_server",)


def _wrap(fn: Any) -> dict[str, Any]:
    try:
        return success_payload(fn())
    except Exception as exc:  # noqa: BLE001
        return error_payload(exc)


def build_server() -> Any:
    from fastmcp import FastMCP

    mcp = FastMCP("lin")

    @mcp.tool()
    def instruct() -> dict[str, Any]:
        return _wrap(instruct_recipe)

    @mcp.tool()
    def note(name: str, version: str = "v2") -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            text = render_note(name, version)
            return {"version": version, "chars": len(text), "note": text}

        return _wrap(_run)

    @mcp.tool()
    def prepare(
        slug: str,
        name: str,
        day: str,
        yes: bool = False,
    ) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            if not yes:
                raise LinValidationError("Refusing to prepare an invite without yes=true")
            profile = load_profile() or Profile()
            draft, _budget = prepare_draft(
                slug=slug,
                name=name,
                day=parse_day(day),
                invites=load_invites(),
                blocked=profile.blocked,
                hard_cap=profile.hard_cap,
                weekly_cap=profile.weekly_cap,
                force=profile.force,
            )
            return draft.model_dump(mode="json")

        return _wrap(_run)

    @mcp.tool()
    def reply() -> dict[str, Any]:
        return _wrap(refuse_reply)

    return mcp
