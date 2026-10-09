# Data engineering

One fact has one writer.

| Fact | Writer | Everyone else |
|------|--------|----------------|
| Profile (label, do-not-contact, caps) | `lin/core/store.py` | reads |
| Session cookie | `lin/core/store.py` | reads, never logs |
| Invite log | `append_invite` | budget reads it |
| Note text | `render_note` | no second template |
| ICP verdict | `score_lead` | prepare calls it |
| Remaining invites | `plan_budget` | counts non-withdrawn rows only |
| Draft | `prepare_draft` | does not append the log |

`prepare` does not write the invite log. A draft is not a sent invite. `lin log --yes` is the only append, and it is idempotent on `(day, slug)`.

There is no LinkedIn response fixture. `fixtures/wire_contracts.json` has an empty `calls` list. `lin send` raises `unsupported` and does not open a connection.

Do not invent an invite body. Do not keep a second copy of who was contacted.
