"""Pydantic schemas for Epic API endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateEpicRequest(BaseModel):
    """Request model for creating an epic (FR-F1)."""
    name: str = Field(..., min_length=1, max_length=255, description="Epic name")
    description: Optional[str] = Field(None, max_length=1000, description="Epic description")
    external_ref: Optional[str] = Field(None, max_length=255, description="External reference (e.g. Jira ID)")


class UpdateEpicRequest(BaseModel):
    """Request model for updating an epic."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    external_ref: Optional[str] = Field(None, max_length=255)


class EpicResponse(BaseModel):
    """Response model for epic information."""
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    external_ref: Optional[str] = None
    created_at: datetime
    feature_count: int = 0
    test_definition_count: int = 0
    active_test_definition_count: int = 0
