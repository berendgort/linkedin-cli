"""Agent recipe. Stable command list for --json clients."""

from __future__ import annotations

from typing import Any

__all__ = ("instruct_recipe",)


def instruct_recipe() -> dict[str, Any]:
    return {
        "name": "lin",
        "objective": (
            "Decide who may be invited and the exact note. "
            "The human sends it on LinkedIn."
        ),
        "never": [
            "send a connection invite",
            "send a post-accept message",
            "send InMail",
            "print the session cookie",
            "send a password",
            "exceed 15 invites in a day",
        ],
        "login": "lin login --cookie <your-session-cookie> --json",
        "flows": [
            "lin note --name 'Ada North' --json",
            "lin score --fixture lead.json --json",
            "lin budget --day 2026-10-09 --json",
            "lin prepare ada-north --name 'Ada North' --day 2026-10-09 --yes --json",
            "lin log ada-north --day 2026-10-09 --yes --json",
        ],
        "writes": "prepare, log, and send do nothing unless --yes is present.",
        "prepare": "Returns the note and the invite URL, then stops.",
        "send": "error_type unsupported. There is no captured invite body.",
        "reply": "Post-accept messages are off. The command always refuses.",
        "ambiguous": "A shared name returns candidates. Pass a slug.",
        "auth": "error_type auth includes human_fix. Do not invent a cookie.",
    }
