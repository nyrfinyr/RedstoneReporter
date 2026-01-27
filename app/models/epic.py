"""Epic model - represents an epic/issue grouping within a project."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.test_case_definition import TestCaseDefinition


class Epic(SQLModel, table=True):
    """Epic model (FR-F1).

    Represents an epic, issue, or functional grouping within a project.
    """
    __tablename__ = "epics"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    external_ref: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: "Project" = Relationship(back_populates="epics")
    test_case_definitions: List["TestCaseDefinition"] = Relationship(
        back_populates="epic",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def test_definition_count(self) -> int:
        """Total number of test case definitions in this epic."""
        return len(self.test_case_definitions) if self.test_case_definitions else 0

    @property
    def active_test_definition_count(self) -> int:
        """Number of active test case definitions in this epic."""
        if not self.test_case_definitions:
            return 0
        return sum(1 for d in self.test_case_definitions if d.is_active)
