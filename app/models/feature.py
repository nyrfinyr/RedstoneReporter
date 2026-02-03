"""Feature document model."""

from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime
from typing import Optional


class Feature(Document):
    """Feature document (FR-N1)."""
    epic_id: Indexed(PydanticObjectId)
    name: str
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "features"
