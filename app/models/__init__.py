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


class Priority(str, Enum):
    """Test case definition priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Import models to ensure they're registered with SQLModel
# Order matters: parent models first to avoid FK resolution issues
from app.models.project import Project
from app.models.epic import Epic
from app.models.test_case_definition import TestCaseDefinition
from app.models.test_run import TestRun
from app.models.test_case import TestCase
from app.models.test_step import TestStep

__all__ = [
    "RunStatus",
    "TestStatus",
    "Priority",
    "Project",
    "Epic",
    "TestCaseDefinition",
    "TestRun",
    "TestCase",
    "TestStep",
]
