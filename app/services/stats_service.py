"""Service layer for statistics calculations."""

from sqlmodel import Session, select, func
from typing import Dict, Any

from app.models import TestRun, TestCase


def calculate_run_statistics(session: Session, run_id: int) -> Dict[str, Any]:
    """Calculate aggregated statistics for a test run.

    Args:
        session: Database session.
        run_id: ID of the test run.

    Returns:
        Dict[str, Any]: Dictionary containing statistics:
            - total_tests: Total number of test cases
            - passed: Number of passed tests
            - failed: Number of failed tests
            - skipped: Number of skipped tests
            - success_rate: Percentage of passed tests (0-100)
            - avg_duration: Average test duration in milliseconds
    """
    # Get test run
    run = session.get(TestRun, run_id)
    if not run:
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "success_rate": 0.0,
            "avg_duration": 0
        }

    # Count by status
    statement = (
        select(
            TestCase.status,
            func.count(TestCase.id).label("count")
        )
        .where(TestCase.run_id == run_id)
        .group_by(TestCase.status)
    )

    results = session.exec(statement).all()

    # Build counts dictionary
    counts = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }

    for status, count in results:
        if status in counts:
            counts[status] = count

    total_tests = sum(counts.values())

    # Calculate success rate
    success_rate = 0.0
    if total_tests > 0:
        success_rate = (counts["passed"] / total_tests) * 100

    # Calculate average duration
    avg_duration_statement = (
        select(func.avg(TestCase.duration))
        .where(TestCase.run_id == run_id)
        .where(TestCase.duration.isnot(None))
    )
    avg_duration = session.exec(avg_duration_statement).first() or 0

    return {
        "total_tests": total_tests,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "success_rate": round(success_rate, 2),
        "avg_duration": int(avg_duration) if avg_duration else 0
    }


def calculate_global_statistics(session: Session) -> Dict[str, Any]:
    """Calculate global statistics across all test runs.

    Args:
        session: Database session.

    Returns:
        Dict[str, Any]: Dictionary containing global statistics.
    """
    # Total runs
    total_runs = session.exec(select(func.count(TestRun.id))).first() or 0

    # Total test cases
    total_cases = session.exec(select(func.count(TestCase.id))).first() or 0

    # Status counts
    statement = (
        select(
            TestCase.status,
            func.count(TestCase.id).label("count")
        )
        .group_by(TestCase.status)
    )

    results = session.exec(statement).all()

    counts = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }

    for status, count in results:
        if status in counts:
            counts[status] = count

    # Success rate
    success_rate = 0.0
    if total_cases > 0:
        success_rate = (counts["passed"] / total_cases) * 100

    return {
        "total_runs": total_runs,
        "total_tests": total_cases,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "success_rate": round(success_rate, 2)
    }
