"""Project document model."""

from beanie import Document, Indexed
from datetime import datetime
from typing import Optional


class Project(Document):
    """Project document (FR-E1)."""
    name: Indexed(str, unique=True)
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "projects"
