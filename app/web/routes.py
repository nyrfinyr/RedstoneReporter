"""Main HTML route handlers for the web UI."""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from typing import Optional
from pathlib import Path

from app.database.session import get_session
from app.services import run_service, case_service, stats_service

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(Path("app/templates")))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    session: Session = Depends(get_session)
):
    """Dashboard page showing list of test runs (FR-D1).

    Args:
        request: FastAPI request object.
        session: Database session.

    Returns:
        HTMLResponse: Rendered dashboard template.
    """
    # Get recent test runs
    runs = run_service.list_runs(session, limit=50)

    # Calculate global statistics
    stats = stats_service.calculate_global_statistics(session)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "runs": runs,
            "stats": stats
        }
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_detail(
    run_id: int,
    request: Request,
    filter: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Run detail page showing test cases (FR-D2, FR-D3, FR-D5).

    Args:
        run_id: ID of the test run.
        request: FastAPI request object.
        filter: Optional status filter ("failed" to show only failed tests).
        session: Database session.

    Returns:
        HTMLResponse: Rendered run detail template.

    Raises:
        HTTPException: If run not found (404).
    """
    # Get test run
    run = run_service.get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    # Get test cases (with optional filter)
    cases = case_service.get_cases_by_run(session, run_id, status_filter=filter)

    # Calculate statistics for this run
    stats = stats_service.calculate_run_statistics(session, run_id)

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
