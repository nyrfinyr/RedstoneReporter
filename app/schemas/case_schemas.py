"""Pydantic schemas for TestCase API endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional


class StepData(BaseModel):
    """Step data within a test case (FR-B3)."""
    description: str = Field(..., min_length=1, max_length=500)
    status: str = Field(..., pattern="^(passed|failed|skipped)$")


class ReportTestCaseRequest(BaseModel):
    """Request model for reporting a test case (FR-B1, FR-B3, FR-B4).

    This will be sent as JSON string in multipart form-data.
    """
    name: str = Field(..., min_length=1, max_length=255)
    status: str = Field(..., pattern="^(passed|failed|skipped)$")
    duration: Optional[int] = Field(None, ge=0, description="Duration in milliseconds")

    # Error details (FR-B4)
    error_message: Optional[str] = Field(None, max_length=1000)
    error_stack: Optional[str] = None

    # Steps (FR-B3)
    steps: List[StepData] = Field(default_factory=list)

    # Optional link to test case definition (FR-H4)
    definition_id: Optional[str] = Field(None, description="Optional TestCaseDefinition ObjectId")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Login Test",
                "status": "passed",
                "duration": 1500,
                "steps": [
                    {"description": "Open page", "status": "passed"},
                    {"description": "Enter credentials", "status": "passed"},
                    {"description": "Click login button", "status": "passed"}
                ]
            }
        }


class ReportTestCaseResponse(BaseModel):
    """Response model for reporting a test case."""
    success: bool
    case_id: str
    message: str = "Test case reported successfully"


class CheckpointResponse(BaseModel):
    """Response model for checkpoint query (FR-C1)."""
    run_id: str
    completed_test_names: List[str]
    total_completed: int

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "507f1f77bcf86cd799439011",
                "completed_test_names": ["Login Test", "Payment Test", "Logout Test"],
                "total_completed": 3
            }
        }
