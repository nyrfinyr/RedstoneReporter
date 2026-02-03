"""Service layer for statistics calculations - async with Beanie."""

from typing import Dict, Any, List
from beanie import PydanticObjectId
from dataclasses import dataclass

from app.models import TestRun, TestCase, Project


@dataclass
class RunWithStats:
    """TestRun with computed statistics for display."""
    id: str
    name: str
    status: str
    start_time: Any
    end_time: Any
    duration: int
    project_id: str
    project: Project
    test_count: int
    passed_count: int
    failed_count: int
    skipped_count: int


async def calculate_run_statistics(run_id: str) -> Dict[str, Any]:
    """Calculate aggregated statistics for a test run."""
    run = await TestRun.get(PydanticObjectId(run_id))
    if not run:
        return {
            "total_tests": 0, "passed": 0, "failed": 0, "skipped": 0,
            "success_rate": 0.0, "avg_duration": 0
        }

    oid = PydanticObjectId(run_id)

    pipeline = [
        {"$match": {"run_id": oid}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "avg_duration": {"$avg": "$duration"}
        }}
    ]
    collection = TestCase.get_pymongo_collection()
    results = await collection.aggregate(pipeline).to_list(length=None)

    counts = {"passed": 0, "failed": 0, "skipped": 0}
    total_duration_sum = 0
    duration_count = 0

    for r in results:
        status = r["_id"]
        if status in counts:
            counts[status] = r["count"]
        if r.get("avg_duration") is not None:
            total_duration_sum += r["avg_duration"] * r["count"]
            duration_count += r["count"]

    total_tests = sum(counts.values())
    success_rate = (counts["passed"] / total_tests * 100) if total_tests > 0 else 0.0
    avg_duration = int(total_duration_sum / duration_count) if duration_count > 0 else 0

    return {
        "total_tests": total_tests,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "success_rate": round(success_rate, 2),
        "avg_duration": avg_duration
    }


async def list_runs_with_stats(limit: int = 50) -> List[RunWithStats]:
    """List test runs with computed statistics for dashboard display."""
    runs = await TestRun.find_all().sort("-start_time").limit(limit).to_list()
    if not runs:
        return []

    # Load projects for runs that have project_id
    project_ids = [run.project_id for run in runs if run.project_id]
    projects_map: Dict[str, Project] = {}
    if project_ids:
        projects = await Project.find({"_id": {"$in": project_ids}}).to_list()
        projects_map = {str(p.id): p for p in projects}

    # Build enriched run objects with stats calculated per-run
    enriched_runs = []
    for run in runs:
        rid = str(run.id)
        project = projects_map.get(str(run.project_id)) if run.project_id else None

        # Count test cases by status for this run
        passed = await TestCase.find({"run_id": run.id, "status": "passed"}).count()
        failed = await TestCase.find({"run_id": run.id, "status": "failed"}).count()
        skipped = await TestCase.find({"run_id": run.id, "status": "skipped"}).count()

        enriched_runs.append(RunWithStats(
            id=rid,
            name=run.name,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
            duration=run.duration or 0,
            project_id=str(run.project_id) if run.project_id else None,
            project=project,
            test_count=passed + failed + skipped,
            passed_count=passed,
            failed_count=failed,
            skipped_count=skipped
        ))

    return enriched_runs


async def calculate_global_statistics() -> Dict[str, Any]:
    """Calculate global statistics across all test runs."""
    total_runs = await TestRun.count()
    total_cases = await TestCase.count()

    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    collection = TestCase.get_pymongo_collection()
    results = await collection.aggregate(pipeline).to_list(length=None)

    counts = {"passed": 0, "failed": 0, "skipped": 0}
    for r in results:
        if r["_id"] in counts:
            counts[r["_id"]] = r["count"]

    success_rate = (counts["passed"] / total_cases * 100) if total_cases > 0 else 0.0

    return {
        "total_runs": total_runs,
        "total_tests": total_cases,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "success_rate": round(success_rate, 2)
    }
