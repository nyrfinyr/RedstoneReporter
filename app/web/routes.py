"""Main HTML route handlers for the web UI."""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pathlib import Path

from app.services import run_service, case_service, stats_service

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(Path("app/templates")))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page showing list of test runs (FR-D1).

    Args:
        request: FastAPI request object.

    Returns:
        HTMLResponse: Rendered dashboard template.
    """
    # Get recent test runs with statistics
    runs = await stats_service.list_runs_with_stats(limit=50)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "runs": runs
        }
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_detail(
    run_id: str,
    request: Request,
    filter: Optional[str] = None
):
    """Run detail page showing test cases (FR-D2, FR-D3, FR-D5).

    Args:
        run_id: ID of the test run.
        request: FastAPI request object.
        filter: Optional status filter ("failed" to show only failed tests).

    Returns:
        HTMLResponse: Rendered run detail template.

    Raises:
        HTTPException: If run not found (404).
    """
    # Get test run
    run = await run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    # Get test cases (with optional filter)
    cases = await case_service.get_cases_by_run(run_id, status_filter=filter)

    # Calculate statistics for this run
    stats = await stats_service.calculate_run_statistics(run_id)

    return templates.TemplateResponse(
        "run_detail.html",
        {
            "request": request,
            "run": run,
            "cases": cases,
            "stats": stats,
            "filter": filter
        }
    )
