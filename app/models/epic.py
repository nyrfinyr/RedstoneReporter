"""Epic model - represents an epic/issue grouping within a project."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.feature import Feature


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
    features: List["Feature"] = Relationship(
        back_populates="epic",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def feature_count(self) -> int:
        """Total number of features in this epic."""
        return len(self.features) if self.features else 0

    @property
    def test_definition_count(self) -> int:
        """Total number of test case definitions across all features."""
        if not self.features:
            return 0
        return sum(f.test_definition_count for f in self.features)

    @property
    def active_test_definition_count(self) -> int:
        """Number of active test case definitions across all features."""
        if not self.features:
            return 0
        return sum(f.active_test_definition_count for f in self.features)
