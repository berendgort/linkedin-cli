# AGENTS.md

`lin` scores a LinkedIn person, drafts the locked note, and stops. The human sends the invite.

Read `docs/objective_function.md`, `docs/code_quality.md`, `docs/data_engineering_standards.md`, and `docs/WIRE.md` before editing.

- Downward layers. 250 lines. Frozen Pydantic. `mypy --strict`. No cookie in output.
- One writer per fact. `prepare` does not append the invite log.
- No fixture, no new wire field. `send` stays `unsupported`.
- `--yes` or the draft and the log do not change.
- Do not send post-accept messages or InMail.
- Do not commit `session.json` or a real invite log.

```bash
python scripts/check_code_quality.py
ruff check .
mypy lin scripts/check_code_quality.py
pytest -q -m "not live"
```

Recipe for callers: `lin instruct --json`.

## Playbook

- [`docs/cli_playbook.md`](docs/cli_playbook.md) — how this stack was built; rate limits and stop rules
