"""Drafts and local logs. Nothing here contacts LinkedIn."""

from __future__ import annotations

from datetime import date
from typing import Any

import typer

from lin.cli.catch import run_cmd
from lin.cli.load import load_json
from lin.core.exceptions import LinValidationError
from lin.core.store import append_invite, load_invites, load_profile
from lin.http.client import send_invite
from lin.models.lead import Invite, InviteStatus, Lead
from lin.models.profile import Profile
from lin.policy.prepare import prepare_draft
from lin.policy.refuse import refuse_inmail, refuse_reply

__all__ = ("register",)


def _rows(fixture: str | None) -> tuple[Invite, ...]:
    if fixture is None:
        return load_invites()
    payload = load_json(fixture)
    if not isinstance(payload, list):
        raise LinValidationError("invites fixture must be a list")
    return tuple(Invite.model_validate(row) for row in payload)


def _prepare(
    slug: str = typer.Argument(...),
    name: str = typer.Option(..., "--name"),
    yes: bool = typer.Option(False, "--yes"),
    day: str = typer.Option(..., "--day"),
    invites: str | None = typer.Option(None, "--invites"),
    lead: str | None = typer.Option(None, "--lead"),
    page_text: str = typer.Option("", "--page-text"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        if not yes:
            raise LinValidationError("Refusing to prepare an invite without --yes")
        profile = load_profile() or Profile()
        person = None
        if lead is not None:
            payload = load_json(lead)
            if not isinstance(payload, dict):
                raise LinValidationError("lead fixture must be an object")
            person = Lead.model_validate(payload)
        draft, _budget = prepare_draft(
            slug=slug,
            name=name,
            day=date.fromisoformat(day),
            invites=_rows(invites),
            blocked=profile.blocked,
            lead=person,
            page_text=page_text,
            hard_cap=profile.hard_cap,
            weekly_cap=profile.weekly_cap,
            force=profile.force,
        )
        return draft.model_dump(mode="json")

    run_cmd(_run, as_json=json_out)


def _log(
    slug: str = typer.Argument(...),
    day: str = typer.Option(..., "--day"),
    yes: bool = typer.Option(False, "--yes"),
    status: str = typer.Option("invited", "--status"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        if not yes:
            raise LinValidationError("Refusing to write the invite log without --yes")
        if status == "invited":
            kind: InviteStatus = "invited"
        elif status == "accepted":
            kind = "accepted"
        elif status == "withdrawn":
            kind = "withdrawn"
        else:
            raise LinValidationError("status must be invited, accepted, or withdrawn")
        rows = append_invite(Invite(day=date.fromisoformat(day), slug=slug, status=kind))
        return {"logged": len(rows), "slug": slug, "day": day}

    run_cmd(_run, as_json=json_out)


def _send(
    slug: str = typer.Argument(...),
    note: str = typer.Option(..., "--note"),
    yes: bool = typer.Option(False, "--yes"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        if not yes:
            raise LinValidationError("Refusing to send without --yes")
        send_invite(slug, note)
        return {"sent": False}

    run_cmd(_run, as_json=json_out)


def _reply(json_out: bool = typer.Option(False, "--json")) -> None:
    def _run() -> dict[str, Any]:
        refuse_reply()
        return {}

    run_cmd(_run, as_json=json_out)


def _inmail(json_out: bool = typer.Option(False, "--json")) -> None:
    def _run() -> dict[str, Any]:
        refuse_inmail()
        return {}

    run_cmd(_run, as_json=json_out)


def register(app: typer.Typer) -> None:
    app.command("prepare")(_prepare)
    app.command("log")(_log)
    app.command("send")(_send)
    app.command("reply")(_reply)
    app.command("inmail")(_inmail)
