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

        # Feature 03: Migrate epic_id → feature_id on test_case_definitions
        # Step 1: Add feature_id column if missing
        cursor.execute("PRAGMA table_info(test_case_definitions)")
        tcd_columns = [col[1] for col in cursor.fetchall()]
        if "feature_id" not in tcd_columns:
            cursor.execute("ALTER TABLE test_case_definitions ADD COLUMN feature_id INTEGER")
            logger.info("Migration: added feature_id column to test_case_definitions")

        # Step 2: For each epic that has test_case_definitions with feature_id=NULL,
        # create a Feature with the same name and link the definitions
        cursor.execute(
            "SELECT DISTINCT d.epic_id, e.name "
            "FROM test_case_definitions d "
            "JOIN epics e ON d.epic_id = e.id "
            "WHERE d.feature_id IS NULL AND d.epic_id IS NOT NULL"
        )
        epics_to_migrate = cursor.fetchall()
        for epic_id, epic_name in epics_to_migrate:
            # Check if a feature already exists for this epic (idempotent)
            cursor.execute(
                "SELECT id FROM features WHERE epic_id = ? AND name = ?",
                (epic_id, epic_name)
            )
            row = cursor.fetchone()
            if row:
                feature_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO features (epic_id, name, created_at) VALUES (?, ?, datetime('now'))",
                    (epic_id, epic_name)
                )
                feature_id = cursor.lastrowid
                logger.info(f"Migration: created Feature '{epic_name}' (id={feature_id}) for Epic {epic_id}")

            # Link all definitions from this epic to the new feature
            cursor.execute(
                "UPDATE test_case_definitions SET feature_id = ? WHERE epic_id = ? AND feature_id IS NULL",
                (feature_id, epic_id)
            )
            logger.info(f"Migration: linked definitions from Epic {epic_id} to Feature {feature_id}")

        conn.commit()
    finally:
        conn.close()
