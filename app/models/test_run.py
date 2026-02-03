"""TestRun document model."""

from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime
from typing import Optional


class TestRun(Document):
    """TestRun document (FR-A1, FR-A2, FR-A3)."""
    name: Indexed(str)
    status: str = "running"
    start_time: datetime = datetime.utcnow()
    end_time: Optional[datetime] = None
    project_id: Optional[PydanticObjectId] = None

    class Settings:
        name = "test_runs"

    @property
    def duration(self) -> Optional[int]:
        """Calculate duration in milliseconds."""
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return None
