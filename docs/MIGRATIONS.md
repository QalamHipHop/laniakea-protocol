# LaniakeA Protocol — Database Migrations

This project uses **Alembic** for managing database schema changes.

## Quick start

```bash
# Apply the latest schema (PostgreSQL)
export DATABASE_URL=postgresql://user:pass@host:5432/laniakea
alembic upgrade head

# Apply the latest schema (SQLite, dev only)
export DATABASE_URL=sqlite:///./laniakea.db
alembic upgrade head
```

## Production (Render)

`render.yaml` already runs `alembic upgrade head` as part of the
`buildCommand`, so every deploy gets the latest schema. The runtime app
honours the `LANIAKEA_RUN_MIGRATIONS=1` env var and skips the legacy
`Base.metadata.create_all` call, preventing drift between Alembic state
and runtime-created tables.

## Authoring a new migration

```bash
# 1. Edit or add a SQLAlchemy model in laniakea/storage/models.py
# 2. Generate the migration (autogenerate)
alembic revision --autogenerate -m "add new table"

# 3. Review the generated file under migrations/versions/
# 4. Apply locally
alembic upgrade head

# 5. Commit + push - Render will apply on the next deploy
```

## Useful commands

| Command | Effect |
|---------|--------|
| `alembic current` | Print the current revision |
| `alembic history --verbose` | Show full migration graph |
| `alembic upgrade +1` | Apply the next pending migration |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back the most recent migration |
| `alembic downgrade base` | Roll back everything |
| `alembic stamp head` | Mark the schema as up-to-date without running migrations |

## Schema

The initial migration (`0001_initial_schema`) creates these tables:

| Table | Purpose |
|-------|---------|
| `blocks` | Persisted blockchain blocks |
| `transactions` | Block-anchored transactions |
| `smart_contracts` | Deployed smart contracts |
| `contract_executions` | Smart-contract call history |
| `cross_chain_bridges` | Cross-chain transfer records |
| `users` | Application user accounts |
| `analytics` | Time-series protocol metrics |

## Notes

*   `migrations/env.py` reads `DATABASE_URL` directly so no credentials are
    ever committed.
*   The same migration runs on PostgreSQL and SQLite; we use
    `sa.func.current_timestamp()` as a dialect-agnostic default.
*   For dev convenience, the legacy `Base.metadata.create_all` path is
    still active when `LANIAKEA_RUN_MIGRATIONS` is **not** set. This lets
    you spin up a local database without first running Alembic.
