"""SQLite database engine setup."""

from sqlmodel import create_engine, SQLModel
from app.config import settings


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
