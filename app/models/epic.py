"""Epic document model."""

from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime
from typing import Optional


class Epic(Document):
    """Epic document (FR-F1)."""
    project_id: Indexed(PydanticObjectId)
    name: str
    description: Optional[str] = None
    external_ref: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "epics"
