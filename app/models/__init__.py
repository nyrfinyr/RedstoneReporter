"""SQLModel database models for RedstoneReporter."""

from enum import Enum


class RunStatus(str, Enum):
    """Test run status enum."""
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"


class TestStatus(str, Enum):
    """Test case/step status enum."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


# Import models to ensure they're registered with SQLModel
from app.models.test_run import TestRun
from app.models.test_case import TestCase
from app.models.test_step import TestStep

__all__ = [
    "RunStatus",
    "TestStatus",
    "TestRun",
    "TestCase",
    "TestStep",
]
