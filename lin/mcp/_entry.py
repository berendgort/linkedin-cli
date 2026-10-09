"""MCP entrypoint."""

from __future__ import annotations

__all__ = ("run",)


def run() -> None:
    from lin.mcp.server import build_server

    build_server().run()
