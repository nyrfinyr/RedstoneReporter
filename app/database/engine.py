"""SQLite database engine setup."""

import sqlite3
import logging

from sqlmodel import create_engine, SQLModel
from app.config import settings

logger = logging.getLogger(__name__)

# Create SQLite engine
# check_same_thread=False is required for SQLite with FastAPI
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)


def create_db_and_tables():
    """Create all database tables if they don't exist.

    This function is called on application startup to ensure
    the database schema is initialized (NFR-04: auto-create if missing).
    """
    SQLModel.metadata.create_all(engine)


def run_migrations():
    """Run lightweight migrations for adding new columns to existing tables (NFR-07).

    SQLModel.metadata.create_all only creates NEW tables; it does NOT add
    columns to existing tables. This function handles that via ALTER TABLE.
    Idempotent: safe to run on every startup.
    """
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add project_id to test_runs (FR-H5)
        cursor.execute("PRAGMA table_info(test_runs)")
        columns = [col[1] for col in cursor.fetchall()]
        if "project_id" not in columns:
            cursor.execute("ALTER TABLE test_runs ADD COLUMN project_id INTEGER")
            logger.info("Migration: added project_id column to test_runs")

        # Add definition_id to test_cases (FR-H4)
        cursor.execute("PRAGMA table_info(test_cases)")
        columns = [col[1] for col in cursor.fetchall()]
        if "definition_id" not in columns:
            cursor.execute("ALTER TABLE test_cases ADD COLUMN definition_id INTEGER")
            logger.info("Migration: added definition_id column to test_cases")

        conn.commit()
    finally:
        conn.close()
