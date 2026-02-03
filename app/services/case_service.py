"""Service layer for TestCase operations - async with Beanie."""

import os
import logging
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId

from app.models import TestCase, TestStepEmbed
from app.services.exceptions import CaseNotFoundError
from app.config import settings

logger = logging.getLogger(__name__)


async def create_test_case(
    run_id: str,
    case_data: Dict[str, Any],
    screenshot_path: Optional[str] = None
) -> TestCase:
    """Create a test case with embedded steps (FR-B1, FR-B3)."""
    steps = [
        TestStepEmbed(
            description=s["description"],
            status=s["status"],
            order_index=idx
        )
        for idx, s in enumerate(case_data.get("steps", []))
    ]

    definition_id = case_data.get("definition_id")

    case = TestCase(
        run_id=PydanticObjectId(run_id),
        name=case_data["name"],
        status=case_data["status"],
        duration=case_data.get("duration"),
        error_message=case_data.get("error_message"),
        error_stack=case_data.get("error_stack"),
        screenshot_path=screenshot_path,
        definition_id=PydanticObjectId(definition_id) if definition_id else None,
        steps=steps
    )
    await case.insert()
    return case


async def get_completed_case_names(run_id: str) -> List[str]:
    """Get list of completed test case names for checkpoint (FR-C1)."""
    cases = await TestCase.find(
        TestCase.run_id == PydanticObjectId(run_id)
    ).to_list()
    return [c.name for c in cases]


async def get_cases_by_run(
    run_id: str,
    status_filter: Optional[str] = None
) -> List[TestCase]:
    """Get all test cases for a run, optionally filtered by status (FR-D5)."""
    query = {"run_id": PydanticObjectId(run_id)}
    if status_filter:
        query["status"] = status_filter
    return await TestCase.find(query).sort("+created_at").to_list()


async def get_case_with_steps(case_id: str) -> Optional[TestCase]:
    """Get a test case with all its steps (steps are embedded)."""
    return await TestCase.get(PydanticObjectId(case_id))


async def get_case_by_id(case_id: str) -> Optional[TestCase]:
    """Get a test case by ID."""
    return await TestCase.get(PydanticObjectId(case_id))


async def get_cases_by_definition(definition_id: str) -> List[TestCase]:
    """Get all test case executions linked to a definition."""
    return await TestCase.find(
        TestCase.definition_id == PydanticObjectId(definition_id)
    ).sort("-created_at").to_list()


async def delete_test_case(case_id: str) -> None:
    """Hard delete a test case with all associated data (FR-O1)."""
    case = await TestCase.get(PydanticObjectId(case_id))
    if not case:
        raise CaseNotFoundError(case_id)

    if case.screenshot_path:
        screenshot_full_path = settings.SCREENSHOT_DIR / case.screenshot_path
        if screenshot_full_path.exists():
            try:
                os.remove(screenshot_full_path)
                logger.info(f"Deleted screenshot: {screenshot_full_path}")
            except OSError as e:
                logger.warning(f"Failed to delete screenshot {screenshot_full_path}: {e}")

    await case.delete()
    logger.info(f"TestCase {case_id} permanently deleted")
