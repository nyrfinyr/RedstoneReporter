"""Pydantic schemas for Project API endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateProjectRequest(BaseModel):
    """Request model for creating a project (FR-E1)."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")


class UpdateProjectRequest(BaseModel):
    """Request model for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectResponse(BaseModel):
    """Response model for project information."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    epic_count: int = 0
    test_definition_count: int = 0
    active_test_definition_count: int = 0
