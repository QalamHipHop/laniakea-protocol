"""
LaniakeA Protocol - SQLAlchemy Database Setup
Initializes the SQLAlchemy engine and session for PostgreSQL.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from laniakea.utils.config import Config

# Base class for declarative models
Base = declarative_base()

# Global engine and session factory
Engine = None
SessionLocal = None

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
        Config.logger.info("✅ SQLAlchemy database connection successful.")

        # Create all tables defined by models inheriting from Base
        # In a production environment, you would use a migration tool like Alembic
        Base.metadata.create_all(bind=Engine)
        Config.logger.info("✅ SQLAlchemy models and tables initialized.")

    except Exception as e:
        Config.logger.error(f"❌ SQLAlchemy database initialization failed: {e}")
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
