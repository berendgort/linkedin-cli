"""Typer entry. Agents pass --json."""

from __future__ import annotations

import typer

from lin.cli import cmd_ops, cmd_read, cmd_write

__all__ = ("app", "cli")

app = typer.Typer(
    name="lin",
    help=(
        "LinkedIn outreach for humans and agents. "
        "Score a person, draft the note, stop before send. "
        "Recipe: lin instruct --json."
    ),
    no_args_is_help=True,
    add_completion=False,
)

cmd_ops.register(app)
cmd_read.register(app)
cmd_write.register(app)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
