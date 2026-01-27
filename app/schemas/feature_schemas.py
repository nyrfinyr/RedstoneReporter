"""Pydantic schemas for Feature API endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateFeatureRequest(BaseModel):
    """Request model for creating a feature (FR-N1)."""
    name: str = Field(..., min_length=1, max_length=255, description="Feature name")
    description: Optional[str] = Field(None, max_length=1000, description="Feature description")


class UpdateFeatureRequest(BaseModel):
    """Request model for updating a feature."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class FeatureResponse(BaseModel):
    """Response model for feature information."""
    id: int
    epic_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    test_definition_count: int = 0
    active_test_definition_count: int = 0

    class Config:
        from_attributes = True
