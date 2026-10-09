"""Setup, login, and the agent recipe."""

from __future__ import annotations

from typing import Any

import typer

from lin import __version__
from lin.cli.catch import run_cmd
from lin.core.exceptions import LinValidationError
from lin.core.instruct import instruct_recipe
from lin.core.paths import lin_home, session_path
from lin.core.slug import check_slug
from lin.core.store import load_profile, load_session, save_profile, save_session
from lin.models.profile import Profile, Session

__all__ = ("register",)


def _instruct(json_out: bool = typer.Option(False, "--json")) -> None:
    run_cmd(instruct_recipe, as_json=json_out)


def _doctor(json_out: bool = typer.Option(False, "--json")) -> None:
    def _run() -> dict[str, Any]:
        profile = load_profile()
        session = load_session()
        mode_ok: bool | None = None
        path = session_path()
        if path.is_file():
            mode_ok = (path.stat().st_mode & 0o777) == 0o600
        return {
            "version": __version__,
            "home": str(lin_home()),
            "profile": profile is not None,
            "session": session is not None,
            "session_mode_ok": mode_ok,
            "blocked": list(profile.blocked) if profile else [],
            "sends": False,
        }

    run_cmd(_run, as_json=json_out)


def _setup(
    label: str = typer.Option("", "--label"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, str]:
        current = load_profile() or Profile()
        save_profile(current.model_copy(update={"label": label}))
        return {"label": label}

    run_cmd(_run, as_json=json_out)


def _login(
    cookie: str = typer.Option(..., "--cookie"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        if not cookie.strip():
            raise LinValidationError("cookie is empty")
        save_session(Session(cookie=cookie.strip()))
        return {"saved": True}

    run_cmd(_run, as_json=json_out)


def _block(
    slug: str = typer.Argument(...),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    def _run() -> dict[str, Any]:
        profile = load_profile() or Profile()
        blocked = tuple(dict.fromkeys((*profile.blocked, check_slug(slug))))
        save_profile(profile.model_copy(update={"blocked": blocked}))
        return {"blocked": list(blocked)}

    run_cmd(_run, as_json=json_out)


def register(app: typer.Typer) -> None:
    app.command("instruct")(_instruct)
    app.command("doctor")(_doctor)
    app.command("setup")(_setup)
    app.command("login")(_login)
    app.command("block")(_block)
