"""Beanie document models for RedstoneReporter."""

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


from app.models.project import Project
from app.models.epic import Epic
from app.models.feature import Feature
from app.models.test_case_definition import TestCaseDefinition
from app.models.test_run import TestRun
from app.models.test_case import TestCase, TestStepEmbed

ALL_DOCUMENT_MODELS = [
    Project,
    Epic,
    Feature,
    TestCaseDefinition,
    TestRun,
    TestCase,
]

__all__ = [
    "RunStatus",
    "TestStatus",
    "Priority",
    "Project",
    "Epic",
    "Feature",
    "TestCaseDefinition",
    "TestRun",
    "TestCase",
    "TestStepEmbed",
    "ALL_DOCUMENT_MODELS",
]
