# Wire

No LinkedIn call is captured. `fixtures/wire_contracts.json` lists zero calls.

`lin send` raises `error_type: unsupported` for that reason. The human opens the URL `prepare` returns:

`https://www.linkedin.com/preload/custom-invite/?vanityName={slug}`

That string is the site path the operator already uses. It is not an API response.

Login stores a cookie the operator pastes. The cookie is not sent anywhere in this version, because there is no fixture to send it to.

Do not add `/voyager/` or an invitation POST until a redacted fixture and a parser test exist. `scripts/check_code_quality.py` fails if those strings appear in `lin/`.
