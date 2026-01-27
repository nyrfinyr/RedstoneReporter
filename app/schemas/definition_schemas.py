"""Pydantic schemas for TestCaseDefinition API endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class StepDefinition(BaseModel):
    """A single step in a test case definition."""
    description: str = Field(..., min_length=1, max_length=500)
    order: int = Field(..., ge=0)


class CreateTestCaseDefinitionRequest(BaseModel):
    """Request model for creating a test case definition (FR-G1)."""
    title: str = Field(..., min_length=1, max_length=255, description="Test case title")
    description: Optional[str] = Field(None, max_length=2000)
    preconditions: Optional[str] = Field(None, max_length=2000)
    steps: List[StepDefinition] = Field(default_factory=list)
    expected_result: Optional[str] = Field(None, max_length=2000)
    priority: str = Field(default="medium", pattern="^(critical|high|medium|low)$")


class UpdateTestCaseDefinitionRequest(BaseModel):
    """Request model for updating a test case definition (FR-G2)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    preconditions: Optional[str] = Field(None, max_length=2000)
    steps: Optional[List[StepDefinition]] = None
    expected_result: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field(None, pattern="^(critical|high|medium|low)$")
    is_active: Optional[bool] = None


class TestCaseDefinitionResponse(BaseModel):
    """Full response model for test case definition."""
    id: int
    epic_id: int
    title: str
    description: Optional[str] = None
    preconditions: Optional[str] = None
    steps: List[dict] = []
    expected_result: Optional[str] = None
    priority: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    execution_count: int = 0

    class Config:
        from_attributes = True


class TestCaseDefinitionListResponse(BaseModel):
    """Lightweight response for listing definitions (without steps)."""
    id: int
    epic_id: int
    title: str
    description: Optional[str] = None
    priority: str
    is_active: bool
    created_at: datetime
    execution_count: int = 0

    class Config:
        from_attributes = True
