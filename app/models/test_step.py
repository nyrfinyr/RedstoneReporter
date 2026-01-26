"""TestStep model - represents a single step within a test case."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.test_case import TestCase


class TestStep(SQLModel, table=True):
    """Test Step model (FR-B3).

    Represents a single step within a test case execution.
    Steps are ordered by order_index.
    """
    __tablename__ = "test_steps"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to TestCase
    case_id: int = Field(foreign_key="test_cases.id", index=True)

    # Step details
    description: str = Field(max_length=500)
    status: str = Field(max_length=50)  # TestStatus enum values
    order_index: int = Field(ge=0)  # Greater than or equal to 0

    # Relationship
    case: "TestCase" = Relationship(back_populates="steps")

    class Config:
        """SQLModel configuration."""
        # Create composite index on (case_id, order_index) for efficient querying
        indexes = [
            {"fields": ["case_id", "order_index"], "unique": False}
        ]
