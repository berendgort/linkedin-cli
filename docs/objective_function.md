# Objective

The operator has one name that passes the ICP, the locked connection note, and a remaining invite budget. The human sends that invite on LinkedIn.

A run is good when all of these are true:

- The note is the locked text with only the name changed, at or under 300 characters, with no em dash.
- A medspa-only profile, a hospital role, or a non-US profile does not pass.
- Two people with the same name return `error_type: ambiguous` and candidates.
- The day stays at or under 15 invites, the soft target, the weekly cap of 80, and the accept-rate gate.
- Someone on the do-not-contact list is refused.
- `prepare --yes` returns the note and the invite URL and sets `stopped_before_send`.
- `send` is `unsupported`. Post-accept replies and InMail are refused.
- The session cookie is never printed.

A green schema that sent the invite, or that invited the wrong person, is a failure.
