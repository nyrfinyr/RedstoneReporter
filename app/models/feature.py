"""Feature model - represents a specific functionality within an epic."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.epic import Epic
    from app.models.test_case_definition import TestCaseDefinition


class Feature(SQLModel, table=True):
    """Feature model (FR-N1).

    Represents a specific functionality within an epic.
    A feature must always belong to an epic.
    """
    __tablename__ = "features"

    id: Optional[int] = Field(default=None, primary_key=True)
    epic_id: int = Field(foreign_key="epics.id", index=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    epic: "Epic" = Relationship(back_populates="features")
    test_case_definitions: List["TestCaseDefinition"] = Relationship(
        back_populates="feature",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def test_definition_count(self) -> int:
        """Total number of test case definitions in this feature."""
        return len(self.test_case_definitions) if self.test_case_definitions else 0

    @property
    def active_test_definition_count(self) -> int:
        """Number of active test case definitions in this feature."""
        if not self.test_case_definitions:
            return 0
        return sum(1 for d in self.test_case_definitions if d.is_active)
