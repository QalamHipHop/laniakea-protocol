"""
Alembic environment configuration for LaniakeA Protocol.

Reads the database URL from the ``DATABASE_URL`` env var (with sensible
fallbacks for local dev) and points metadata discovery at every SQLAlchemy
declarative model that uses ``Base`` from ``laniakea.storage.database_setup``.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

import sqlalchemy as sa
from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the project root is on sys.path when alembic is run from CLI
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Import the declarative Base + all models so metadata.create_all sees them
from laniakea.storage.database_setup import Base
from laniakea.storage import models  # noqa: F401 - import for metadata registration

config = context.config

# Configure Python logging from alembic.ini (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject database URL from env so we never commit credentials
database_url = os.getenv(
    "DATABASE_URL",
    "sqlite:///./laniakea.db",  # safe default for `alembic` CLI in dev
)
# SQLAlchemy 1.4+ requires postgresql:// not postgres://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", database_url)


def _patch_now_defaults(metadata) -> None:
    """Translate PostgreSQL ``now()`` defaults to SQLite-friendly ones.

    The migration file uses ``server_default=sa.text("now()")`` because that
    is the canonical PostgreSQL form. SQLite does not understand ``now()``,
    so we rewrite the default on the ``Column`` objects to
    ``CURRENT_TIMESTAMP`` when the bound dialect is sqlite.
    """
    if not database_url.startswith("sqlite"):
        return

    for table in metadata.tables.values():
        for column in table.columns:
            default = column.server_default
            if default is not None:
                arg = getattr(default, "arg", None)
                if isinstance(arg, str) and arg.lower().startswith("now"):
                    column.server_default = sa.text("CURRENT_TIMESTAMP")


# Metadata for autogenerate
target_metadata = Base.metadata
_patch_now_defaults(target_metadata)


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (emits SQL)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database engine."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
