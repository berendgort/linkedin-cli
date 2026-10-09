# Code quality

These rules are the bar. `scripts/check_code_quality.py` enforces the ones a script can see. `mypy --strict` enforces the types.

## Layers

Imports point downward. A module may import the same rank or a lower rank.

| Rank | Package | Owns |
|------|---------|------|
| 10 | `lin/models` | Frozen Pydantic DTOs. No I/O. |
| 15 | `lin/core/exceptions` | Error types. |
| 20 | `lin/http` | The send stub. It raises `unsupported`. No CLI imports. |
| 30 | `lin/core` | Envelope, paths, the profile and invite-log store, instruct. |
| 40 | `lin/policy` | Note, ICP, budget, draft. No HTTP. |
| 50 | `lin/cli`, `lin/mcp` | Typer and FastMCP. They do not import each other. |

## File and function rules

- 250 lines or fewer per file under `lin/`.
- No work at import time. No network, no file reads, no prints in library modules.
- `print` is allowed only in `lin/cli/catch.py`.
- No em dash or en dash in Python.
- Every module has `__all__`.
- Public models are frozen Pydantic models.
- `mypy --strict` is clean.
- Fail closed with a typed exception. The envelope sets `error_type` and `retryable`.
- Do not log or print the session cookie. Session files are mode `0600`.

## Gate

```bash
python scripts/check_code_quality.py
ruff check .
mypy lin scripts/check_code_quality.py
pytest -q -m "not live"
```
