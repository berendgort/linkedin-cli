# lin

LinkedIn outreach CLI for humans and agents. Score a person, draft the locked note, and stop before send.

```bash
pipx install 'linkedin-cli[mcp] @ git+https://github.com/berendgort/linkedin-cli.git'
lin instruct --json
lin note --name "Ada North" --json
lin score --fixture lead.json --json
lin prepare ada-north --name "Ada North" --day 2026-06-03 --yes --json
```

`lin prepare --yes` returns the note and the invite URL. It does not send. `lin send` is `unsupported` until an invite fixture exists. `lin reply` and `lin inmail` always refuse.

Paste your own session cookie with `lin login --cookie`. Do not put a password in the command.

## For AI agents

1. Run `lin instruct --json` and follow `data.flows`.
2. Pass `--json` on every command. Read `ok`, `error_type`, `retryable`.
3. `ambiguous` includes `candidates`. Ask for a slug.
4. `auth` includes `human_fix`. Do not invent a cookie.
5. `prepare` without `--yes` returns `validation_error` and writes nothing.
6. `prepare --yes` sets `stopped_before_send`. Stop there. Do not call `send`.

## Quality gate

```bash
python scripts/check_code_quality.py
ruff check .
mypy lin scripts/check_code_quality.py
pytest -q -m "not live"
```
