"""Service layer for TestCase operations."""

from sqlmodel import Session, select
from typing import List, Optional, Dict, Any

from app.models import TestCase, TestStep


def create_test_case(
    session: Session,
    run_id: int,
    case_data: Dict[str, Any],
    screenshot_path: Optional[str] = None
) -> TestCase:
    """Create a test case with steps atomically (FR-B1, FR-B3).

    This function creates both the test case and its steps in a single
    transaction to ensure atomicity.

    Args:
        session: Database session.
        run_id: ID of the parent test run.
        case_data: Dictionary containing test case data:
            - name (str): Test case name
            - status (str): Test status (passed/failed/skipped)
            - duration (int, optional): Duration in milliseconds
            - error_message (str, optional): Error message if failed
            - error_stack (str, optional): Stack trace if failed
            - steps (List[dict], optional): List of step dictionaries
        screenshot_path: Relative path to screenshot file (FR-B5).

    Returns:
        TestCase: The created test case with all steps.

    Example:
        case_data = {
            "name": "Login Test",
            "status": "passed",
            "duration": 1500,
            "steps": [
                {"description": "Open page", "status": "passed"},
                {"description": "Click login", "status": "passed"}
            ]
        }
    """
    # Create test case
    case = TestCase(
        run_id=run_id,
        name=case_data["name"],
        status=case_data["status"],
        duration=case_data.get("duration"),
        error_message=case_data.get("error_message"),
        error_stack=case_data.get("error_stack"),
        screenshot_path=screenshot_path
    )
    session.add(case)
    session.flush()  # Get case.id without committing

    # Create steps (FR-B3)
    for idx, step_data in enumerate(case_data.get("steps", [])):
        step = TestStep(
            case_id=case.id,
            description=step_data["description"],
            status=step_data["status"],
            order_index=idx
        )
        session.add(step)

    # Commit transaction atomically
    session.commit()
    session.refresh(case)
    return case


def get_completed_case_names(session: Session, run_id: int) -> List[str]:
    """Get list of completed test case names for checkpoint (FR-C1).

    This enables the AI agent to query which tests have already been
    completed in case of crash/restart.

    Args:
        session: Database session.
        run_id: ID of the test run.

    Returns:
        List[str]: List of test case names that have been completed.
    """
    statement = select(TestCase.name).where(TestCase.run_id == run_id)
    results = session.exec(statement).all()
    return list(results)


def get_cases_by_run(
    session: Session,
    run_id: int,
    status_filter: Optional[str] = None
) -> List[TestCase]:
    """Get all test cases for a run, optionally filtered by status (FR-D5).

    Args:
        session: Database session.
        run_id: ID of the test run.
        status_filter: Optional status to filter by (e.g., "failed").

    Returns:
        List[TestCase]: List of test cases.
    """
    statement = select(TestCase).where(TestCase.run_id == run_id)

    if status_filter:
        statement = statement.where(TestCase.status == status_filter)

    statement = statement.order_by(TestCase.created_at)

    results = session.exec(statement)
    return list(results)


def get_case_with_steps(session: Session, case_id: int) -> Optional[TestCase]:
    """Get a test case with all its steps loaded.

    Args:
        session: Database session.
        case_id: ID of the test case.

    Returns:
        Optional[TestCase]: The test case with steps, or None if not found.
    """
    case = session.get(TestCase, case_id)
    if case:
        # Access steps to ensure they're loaded
        _ = case.steps
    return case


def get_case_by_id(session: Session, case_id: int) -> Optional[TestCase]:
    """Get a test case by ID.

    Args:
        session: Database session.
        case_id: ID of the test case.

    Returns:
        Optional[TestCase]: The test case if found, None otherwise.
    """
    return session.get(TestCase, case_id)
