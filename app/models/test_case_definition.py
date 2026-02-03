"""TestCaseDefinition document model."""

from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime
from typing import Optional, List


class TestCaseDefinition(Document):
    """TestCaseDefinition document (FR-G1)."""
    feature_id: Indexed(PydanticObjectId)
    title: str
    description: Optional[str] = None
    preconditions: Optional[str] = None
    steps: List[dict] = []
    expected_result: Optional[str] = None
    priority: str = "medium"
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "test_case_definitions"
