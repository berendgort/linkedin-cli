"""Read-only note, score, budget, and name resolution."""

from __future__ import annotations

from datetime import date
from typing import Any

import typer

from lin.cli.catch import run_cmd
from lin.cli.load import load_json
from lin.core.exceptions import LinValidationError
from lin.core.store import load_invites
from lin.models.lead import Invite, Lead
from lin.policy.budget import plan_budget
from lin.policy.icp import score_lead
from lin.policy.note import render_note
from lin.policy.resolve import resolve_leads

__all__ = ("register",)


def _invites(fixture: str | None) -> tuple[Invite, ...]:
    if fixture is None:
        return load_invites()
    payload = load_json(fixture)
    if not isinstance(payload, list):
        raise LinValidationError("invites fixture must be a list")
    return tuple(Invite.model_validate(row) for row in payload)


def _leads(fixture: str) -> list[Lead]:
    payload = load_json(fixture)
    if not isinstance(payload, list):
        raise LinValidationError("bench fixture must be a list")
    return [Lead.model_validate(row) for row in payload]


def _note(
    name: str = typer.Option(..., "--name"),
    version: str = typer.Option("v2", "--version"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        text = render_note(name, version)
        return {"version": version, "chars": len(text), "note": text}

    run_cmd(_run, as_json=json_out)


def _score(
    fixture: str = typer.Option(..., "--fixture"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        payload = load_json(fixture)
        if not isinstance(payload, dict):
            raise LinValidationError("lead fixture must be an object")
        return score_lead(Lead.model_validate(payload)).model_dump(mode="json")

    run_cmd(_run, as_json=json_out)


def _budget(
    day: str = typer.Option(..., "--day"),
    fixture: str | None = typer.Option(None, "--fixture"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        when = date.fromisoformat(day)
        report = plan_budget(when, _invites(fixture))
        return report.model_dump(mode="json")

    run_cmd(_run, as_json=json_out)


def _who(
    query: str = typer.Argument(...),
    bench: str = typer.Option(..., "--bench"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        return resolve_leads(query, _leads(bench)).model_dump(mode="json")

    run_cmd(_run, as_json=json_out)


def register(app: typer.Typer) -> None:
    app.command("note")(_note)
    app.command("score")(_score)
    app.command("budget")(_budget)
    app.command("who")(_who)
