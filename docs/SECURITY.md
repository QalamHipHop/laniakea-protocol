# LaniakeA Protocol — Security Policy

**Contact:** LaniakeA Dev (`dev@laniakea-protocol.org`)

## Reporting a Vulnerability

Please **do not** file a public issue. Email `dev@laniakea-protocol.org`
with:

- Description and impact
- Reproduction steps
- Affected version / commit

We aim to acknowledge within **72 hours**.

## Cryptography

- Wallet keys use `cryptography` EC (secp256k1) primitives.
- The wallet encryption key **must** be supplied via the
  `LANIAKEA_WALLET_ENCRYPTION_KEY` env var — never hardcode it.
- Default placeholder keys are rejected at runtime.

## Operational Hardening

- The default Render deploy binds `0.0.0.0:8000`; put it behind a reverse
  proxy (see `nginx/`) with TLS termination.
- CORS is configured in `laniakea/api/main.py`. Tighten the allow-list
  before going fully public.
- Rate-limiting is recommended via `fastapi-limiter` (already in
  `requirements.txt`).

## Secrets

Never commit `.env` to git. The repository's `.gitignore` already excludes
it, but double-check before pushing.
