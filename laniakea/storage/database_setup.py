"""
LaniakeA Protocol - SQLAlchemy Database Setup
Initializes the SQLAlchemy engine and session for PostgreSQL.
"""

import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from laniakea.core.config import settings

# Base class for declarative models
Base = declarative_base()

# Global engine and session factory
Engine = None
SessionLocal = None

# Module-level logger — the old ``Config.logger`` attribute never existed
# and was a latent bug, so we use a real stdlib logger here.
logger = logging.getLogger("laniakea.storage.database_setup")


def init_db(db_url: str):
    """
    Initialize the PostgreSQL database connection using SQLAlchemy.

    Args:
        db_url (str): The database connection URL.
    """
    global Engine, SessionLocal

    if not db_url:
        raise ValueError("Database URL is not set. Please configure it in your .env file.")

    try:
        # Create the SQLAlchemy engine
        Engine = create_engine(db_url, pool_pre_ping=True)

        # Create a configured "Session" class
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

        # Test the database connection
        with Engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("SQLAlchemy database connection successful url=%s", db_url)

        # Schema management:
        #   - In production (``LANIAKEA_RUN_MIGRATIONS=1``) the schema is
        #     managed by Alembic (``alembic upgrade head``) so we MUST NOT
        #     also call ``create_all`` to avoid drift.
        #   - In dev / test we still allow the legacy auto-create shortcut.
        if os.getenv("LANIAKEA_RUN_MIGRATIONS") == "1":
            logger.info(
                "LANIAKEA_RUN_MIGRATIONS=1 set - schema is managed by Alembic. "
                "Skipping Base.metadata.create_all."
            )
        else:
            Base.metadata.create_all(bind=Engine)
            logger.info("SQLAlchemy models and tables initialized.")

    except Exception as e:
        logger.error("SQLAlchemy database initialization failed: %s", e)
        raise

def get_db():
    """
    FastAPI dependency to get a database session.
    Ensures the session is closed after the request is finished.
    """
    if not SessionLocal:
        raise RuntimeError("Database is not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
