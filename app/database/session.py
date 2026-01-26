"""Database session management for FastAPI dependency injection."""

from sqlmodel import Session
from app.database.engine import engine
from typing import Generator


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions.

    Yields:
        Session: SQLModel session for database operations.

    Usage:
        @app.get("/endpoint")
        def my_endpoint(session: Session = Depends(get_session)):
            # Use session here
            pass
    """
    with Session(engine) as session:
        yield session
