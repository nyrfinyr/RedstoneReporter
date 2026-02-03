"""Service layer for TestRun operations - async with Beanie."""

from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId

from app.models import TestRun, RunStatus


async def create_run(name: str, project_id: Optional[str] = None) -> TestRun:
    """Create a new test run (FR-A1, FR-H5)."""
    run = TestRun(
        name=name,
        status=RunStatus.RUNNING.value,
        start_time=datetime.utcnow(),
        project_id=PydanticObjectId(project_id) if project_id else None
    )
    await run.insert()
    return run


async def get_run(run_id: str) -> Optional[TestRun]:
    """Get a test run by ID."""
    return await TestRun.get(PydanticObjectId(run_id))


async def finish_run(run_id: str) -> TestRun:
    """Mark a test run as completed (FR-A3)."""
    run = await TestRun.get(PydanticObjectId(run_id))
    if not run:
        raise ValueError(f"Test run with id {run_id} not found")
    if run.status == RunStatus.COMPLETED.value:
        raise ValueError(f"Test run {run_id} is already completed")

    run.status = RunStatus.COMPLETED.value
    run.end_time = datetime.utcnow()
    await run.save()
    return run


async def list_runs(limit: int = 50) -> List[TestRun]:
    """List test runs ordered by start time (most recent first)."""
    return await TestRun.find_all().sort("-start_time").limit(limit).to_list()


async def abort_run(run_id: str) -> TestRun:
    """Mark a test run as aborted."""
    run = await TestRun.get(PydanticObjectId(run_id))
    if not run:
        raise ValueError(f"Test run with id {run_id} not found")

    run.status = RunStatus.ABORTED.value
    run.end_time = datetime.utcnow()
    await run.save()
    return run
