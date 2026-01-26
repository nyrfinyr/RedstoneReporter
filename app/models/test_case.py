"""TestCase model - represents a single test case execution."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.test_run import TestRun
    from app.models.test_step import TestStep


class TestCase(SQLModel, table=True):
    """Test Case model (FR-B1, FR-B3, FR-B4, FR-B5).

    Represents a single test case result with optional screenshot.
    """
    __tablename__ = "test_cases"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to TestRun
    run_id: int = Field(foreign_key="test_runs.id", index=True)

    # Test case details
    name: str = Field(max_length=255, index=True)
    status: str = Field(max_length=50)  # TestStatus enum values
    duration: Optional[int] = None  # Duration in milliseconds

    # Error details (FR-B4)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    error_stack: Optional[str] = Field(default=None)  # SQLModel maps Optional[str] to TEXT automatically

    # Screenshot path (FR-B5 - relative path, not full path)
    screenshot_path: Optional[str] = Field(default=None, max_length=500)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    run: "TestRun" = Relationship(back_populates="cases")
    steps: List["TestStep"] = Relationship(
        back_populates="case",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def has_screenshot(self) -> bool:
        """Check if test case has an associated screenshot.

        Returns:
            bool: True if screenshot_path is set.
        """
        return bool(self.screenshot_path)

    @property
    def step_count(self) -> int:
        """Total number of steps in this test case.

        Returns:
            int: Count of all steps.
        """
        return len(self.steps) if self.steps else 0
