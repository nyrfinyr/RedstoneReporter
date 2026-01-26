"""TestRun model - represents a test execution session."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.test_case import TestCase


class TestRun(SQLModel, table=True):
    """Test Run model (FR-A1, FR-A2, FR-A3).

    Represents a complete test execution session initiated by the AI agent.
    """
    __tablename__ = "test_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    status: str = Field(default="running", max_length=50)  # RunStatus enum values
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    # Relationships
    cases: List["TestCase"] = Relationship(
        back_populates="run",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def duration(self) -> Optional[int]:
        """Calculate duration in milliseconds.

        Returns:
            Optional[int]: Duration in milliseconds, or None if run not completed.
        """
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return None

    @property
    def test_count(self) -> int:
        """Total number of test cases in this run.

        Returns:
            int: Count of all test cases.
        """
        return len(self.cases) if self.cases else 0

    @property
    def passed_count(self) -> int:
        """Number of passed test cases.

        Returns:
            int: Count of test cases with status='passed'.
        """
        if not self.cases:
            return 0
        return sum(1 for case in self.cases if case.status == "passed")

    @property
    def failed_count(self) -> int:
        """Number of failed test cases.

        Returns:
            int: Count of test cases with status='failed'.
        """
        if not self.cases:
            return 0
        return sum(1 for case in self.cases if case.status == "failed")

    @property
    def skipped_count(self) -> int:
        """Number of skipped test cases.

        Returns:
            int: Count of test cases with status='skipped'.
        """
        if not self.cases:
            return 0
        return sum(1 for case in self.cases if case.status == "skipped")
