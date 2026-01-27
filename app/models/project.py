"""Project model - represents a software project or functional area."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.epic import Epic
    from app.models.test_run import TestRun


class Project(SQLModel, table=True):
    """Project model (FR-E1).

    Represents a software project or functional area.
    """
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, unique=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    epics: List["Epic"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    runs: List["TestRun"] = Relationship(back_populates="project")

    @property
    def epic_count(self) -> int:
        """Total number of epics in this project."""
        return len(self.epics) if self.epics else 0

    @property
    def test_definition_count(self) -> int:
        """Total number of test case definitions across all epics."""
        if not self.epics:
            return 0
        return sum(len(e.test_case_definitions) for e in self.epics if e.test_case_definitions)

    @property
    def active_test_definition_count(self) -> int:
        """Number of active test case definitions across all epics."""
        if not self.epics:
            return 0
        count = 0
        for epic in self.epics:
            if epic.test_case_definitions:
                count += sum(1 for d in epic.test_case_definitions if d.is_active)
        return count
