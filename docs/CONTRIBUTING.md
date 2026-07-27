# Contributing to LaniakeA Protocol

**Maintainer:** LaniakeA Dev

Thanks for your interest in LaniakeA! This protocol is intentionally
ambitious — every contribution, from a typo fix to a new consensus rule,
helps the project move forward.

## Quick Path

1. Fork & branch off `main`.
2. Make your change (keep PRs focused and small).
3. `pytest -q` must pass.
4. `black . && flake8 .` must be clean.
5. Open a PR with a clear description and link to any related issue.

## Areas Where Help is Welcome

- New SCDA evolution dynamics
- New consensus primitives under `laniakea/consensus/`
- Additional `/api/*` endpoints and tests
- Frontend visualizations under `web/`
- Documentation under `docs/`

## Reporting Bugs

Open a GitHub issue with:

- Expected vs actual behaviour
- Minimal reproduction
- Logs / stack trace
- Environment (Python version, OS, deployment mode)

## Security

See `docs/SECURITY.md`. Do **not** file public issues for vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under
the project's MIT License.
