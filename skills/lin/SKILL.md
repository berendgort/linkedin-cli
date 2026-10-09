---
name: lin
description: Drive the lin CLI for LinkedIn invite drafts. Use when the user wants a connection note, an ICP check, or a daily invite budget. Never send the invite.
---

# lin

The note and the person are right, or the command fails. The human sends the invite on LinkedIn.

```bash
lin instruct --json
lin note --name "Ada North" --json
lin score --fixture lead.json --json
lin prepare <slug> --name "Ada North" --day YYYY-MM-DD --yes --json
```

- Always pass `--json`.
- `error_type: ambiguous` means show `candidates` and wait for a slug.
- Without `--yes`, do not retry `prepare` as if it wrote something.
- `stopped_before_send` means stop. Do not call `lin send`.
- `lin reply` and `lin inmail` refuse. Leave them refused.
