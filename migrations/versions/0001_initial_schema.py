"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-25 00:13:00.000000

Creates the complete LaniakeA Protocol database schema:
- blocks
- transactions
- smart_contracts
- contract_executions
- cross_chain_bridges
- users
- analytics

This is the initial migration that supersedes the legacy ``Base.metadata.create_all``
runtime schema creation. After running ``alembic upgrade head`` the application
will not auto-create tables anymore.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the LaniakeA Protocol schema.

    Uses ``sa.func.current_timestamp()`` (dialect-agnostic) for the
    ``created_at`` / ``updated_at`` defaults so the same migration works
    on both PostgreSQL and SQLite.
    """
    now = sa.func.current_timestamp()

    op.create_table(
        "blocks",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("block_hash", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("previous_hash", sa.String(length=255)),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("nonce", sa.BigInteger()),
        sa.Column("difficulty", sa.Float()),
        sa.Column("miner_id", sa.String(length=255)),
        sa.Column("transactions_count", sa.Integer()),
        sa.Column("data", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("tx_hash", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("block_hash", sa.String(length=255), sa.ForeignKey("blocks.block_hash")),
        sa.Column("sender", sa.String(length=255), nullable=False),
        sa.Column("receiver", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("fee", sa.Float()),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=50)),
        sa.Column("data", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
    )

    op.create_table(
        "smart_contracts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("contract_address", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("owner_address", sa.String(length=255), nullable=False),
        sa.Column("code", sa.Text()),
        sa.Column("state", sa.JSON()),
        sa.Column("gas_limit", sa.Integer()),
        sa.Column("balance", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=now),
    )

    op.create_table(
        "contract_executions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("contract_address", sa.String(length=255), sa.ForeignKey("smart_contracts.contract_address")),
        sa.Column("function_name", sa.String(length=255)),
        sa.Column("caller_address", sa.String(length=255)),
        sa.Column("gas_used", sa.Integer()),
        sa.Column("result", sa.JSON()),
        sa.Column("status", sa.String(length=50)),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
    )

    op.create_table(
        "cross_chain_bridges",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("bridge_id", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("from_chain", sa.String(length=50), nullable=False),
        sa.Column("to_chain", sa.String(length=50), nullable=False),
        sa.Column("from_address", sa.String(length=255)),
        sa.Column("to_address", sa.String(length=255)),
        sa.Column("amount", sa.Float()),
        sa.Column("token_address", sa.String(length=255)),
        sa.Column("status", sa.String(length=50)),
        sa.Column("from_tx_hash", sa.String(length=255)),
        sa.Column("to_tx_hash", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=now),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(length=255)),
        sa.Column("wallet_address", sa.String(length=255), unique=True),
        sa.Column("balance", sa.Float(), server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=now),
    )

    op.create_table(
        "analytics",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("metric_name", sa.String(length=255), index=True),
        sa.Column("metric_value", sa.Float()),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("data", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=now),
    )


def downgrade() -> None:
    """Drop the LaniakeA Protocol schema."""
    op.drop_table("analytics")
    op.drop_table("users")
    op.drop_table("cross_chain_bridges")
    op.drop_table("contract_executions")
    op.drop_table("smart_contracts")
    op.drop_table("transactions")
    op.drop_table("blocks")
