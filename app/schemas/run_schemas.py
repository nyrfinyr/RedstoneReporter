"""Pydantic schemas for TestRun API endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StartRunRequest(BaseModel):
    """Request model for starting a new test run (FR-A1, FR-H5)."""
    name: str = Field(..., min_length=1, max_length=255, description="Test run name/title")
    project_id: Optional[str] = Field(None, description="Optional project ObjectId")


class RunResponse(BaseModel):
    """Response model for test run information."""
    id: str
    name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # milliseconds
    project_id: Optional[str] = None

    # Statistics (computed in service layer)
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0


class FinishRunResponse(BaseModel):
    """Response model for finishing a test run (FR-A3)."""
    id: str
    name: str
    status: str
    start_time: datetime
    end_time: datetime
    duration: int  # milliseconds
    total_tests: int
    passed: int
    failed: int
    skipped: int
    success_rate: float  # percentage
