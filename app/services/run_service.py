"""Service layer for TestRun operations."""

from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List

from app.models import TestRun, RunStatus


def create_run(session: Session, name: str) -> TestRun:
    """Create a new test run (FR-A1).

    Args:
        session: Database session.
        name: Name/title for the test run.

    Returns:
        TestRun: The created test run with assigned ID.
    """
    run = TestRun(
        name=name,
        status=RunStatus.RUNNING.value,
        start_time=datetime.utcnow()
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def get_run(session: Session, run_id: int) -> Optional[TestRun]:
    """Get a test run by ID.

    Args:
        session: Database session.
        run_id: ID of the test run.

    Returns:
        Optional[TestRun]: The test run if found, None otherwise.
    """
    return session.get(TestRun, run_id)


def finish_run(session: Session, run_id: int) -> TestRun:
    """Mark a test run as completed and calculate statistics (FR-A3).

    Args:
        session: Database session.
        run_id: ID of the test run to finish.

    Returns:
        TestRun: The updated test run.

    Raises:
        ValueError: If run not found or already completed.
    """
    run = session.get(TestRun, run_id)
    if not run:
        raise ValueError(f"Test run with id {run_id} not found")

    if run.status == RunStatus.COMPLETED.value:
        raise ValueError(f"Test run {run_id} is already completed")

    run.status = RunStatus.COMPLETED.value
    run.end_time = datetime.utcnow()

    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def list_runs(session: Session, limit: int = 50) -> List[TestRun]:
    """List test runs ordered by start time (most recent first).

    Args:
        session: Database session.
        limit: Maximum number of runs to return.

    Returns:
        List[TestRun]: List of test runs.
    """
    statement = (
        select(TestRun)
        .order_by(TestRun.start_time.desc())
        .limit(limit)
    )
    results = session.exec(statement)
    return list(results)


def abort_run(session: Session, run_id: int) -> TestRun:
    """Mark a test run as aborted (for error cases).

    Args:
        session: Database session.
        run_id: ID of the test run to abort.

    Returns:
        TestRun: The updated test run.

    Raises:
        ValueError: If run not found.
    """
    run = session.get(TestRun, run_id)
    if not run:
        raise ValueError(f"Test run with id {run_id} not found")

    run.status = RunStatus.ABORTED.value
    run.end_time = datetime.utcnow()

    session.add(run)
    session.commit()
    session.refresh(run)
    return run
