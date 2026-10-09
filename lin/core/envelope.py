"""JSON envelope shared by the CLI and MCP."""

from __future__ import annotations

from typing import Any

from lin.core.errors import classify_error
from lin.core.exceptions import LinAmbiguousError, LinAuthError, LinUnsupportedError

__all__ = ("API_VERSION", "error_payload", "success_payload")

API_VERSION = 1

_LOGIN = (
    "lin login --cookie <your-session-cookie> --json. "
    "Paste your own cookie. Never paste a password."
)
_SEND = (
    "Open data.url and send the note yourself. "
    "This CLI has no invite fixture, so it never sends."
)


def success_payload(data: Any) -> dict[str, Any]:
    return {"ok": True, "api_version": API_VERSION, "data": data}


def error_payload(exc: BaseException) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "api_version": API_VERSION,
        "error": str(exc),
        **classify_error(exc).as_fields(),
    }
    if isinstance(exc, LinAmbiguousError):
        payload["candidates"] = [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in exc.candidates
        ]
    if isinstance(exc, LinAuthError):
        payload["human_fix"] = _LOGIN
    if isinstance(exc, LinUnsupportedError):
        payload["human_fix"] = _SEND
    return payload
