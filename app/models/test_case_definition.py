"""TestCaseDefinition model - represents a predefined test case specification."""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.feature import Feature
    from app.models.test_case import TestCase


class TestCaseDefinition(SQLModel, table=True):
    """TestCaseDefinition model (FR-G1).

    Represents the specification of a test case, defined before execution.
    Steps are stored as JSON: [{"description": "...", "order": 0}, ...]
    """
    __tablename__ = "test_case_definitions"

    id: Optional[int] = Field(default=None, primary_key=True)
    feature_id: int = Field(foreign_key="features.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    preconditions: Optional[str] = Field(default=None, max_length=2000)
    steps: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    expected_result: Optional[str] = Field(default=None, max_length=2000)
    priority: str = Field(default="medium", max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    feature: "Feature" = Relationship(back_populates="test_case_definitions")
    executions: List["TestCase"] = Relationship(back_populates="definition")

    @property
    def execution_count(self) -> int:
        """Total number of test case executions linked to this definition."""
        return len(self.executions) if self.executions else 0
