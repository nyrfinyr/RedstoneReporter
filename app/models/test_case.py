"""TestCase document model with embedded TestStep."""

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TestStepEmbed(BaseModel):
    """Embedded test step (no separate collection)."""
    description: str
    status: str
    order_index: int


class TestCase(Document):
    """TestCase document (FR-B1)."""
    run_id: Indexed(PydanticObjectId)
    name: Indexed(str)
    status: str
    duration: Optional[int] = None
    error_message: Optional[str] = None
    error_stack: Optional[str] = None
    screenshot_path: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    definition_id: Optional[PydanticObjectId] = None
    steps: List[TestStepEmbed] = []

    class Settings:
        name = "test_cases"

    @property
    def has_screenshot(self) -> bool:
        """Check if test case has an associated screenshot."""
        return bool(self.screenshot_path)

    @property
    def step_count(self) -> int:
        """Total number of steps in this test case."""
        return len(self.steps)
