"""HTMX partial route handlers for dynamic UI updates (FR-D4)."""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from typing import Optional

from app.database.session import get_session
from app.services import run_service, case_service, stats_service

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(Path("app/templates")))

router = APIRouter()


@router.get("/runs", response_class=HTMLResponse)
async def get_runs_partial(
    request: Request,
    session: Session = Depends(get_session)
):
    """HTMX partial for auto-refreshing runs list on dashboard.

    This endpoint is called every 5 seconds by HTMX polling to update
    the runs list without full page reload.

    Args:
        request: FastAPI request object.
        session: Database session.

    Returns:
        HTMLResponse: Rendered runs list partial.
    """
    runs = run_service.list_runs(session, limit=50)

    return templates.TemplateResponse(
        "partials/run_list.html",
        {
            "request": request,
            "runs": runs
        }
    )


@router.get("/runs/{run_id}/content", response_class=HTMLResponse)
async def get_run_detail_content(
    run_id: int,
    request: Request,
    filter: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """HTMX partial for auto-refreshing run detail content (FR-I1, FR-I2).

    This endpoint is called every 3 seconds by HTMX polling to update
    the run detail page (stats, test cases) without full page reload.
    When the run status changes from 'running' to 'completed', the returned
    partial will not include hx-trigger, stopping the polling automatically.

    Args:
        run_id: ID of the test run.
        request: FastAPI request object.
        filter: Optional status filter ("failed" to show only failed tests).
        session: Database session.

    Returns:
        HTMLResponse: Rendered run detail content partial.
    """
    run = run_service.get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    cases = case_service.get_cases_by_run(session, run_id, status_filter=filter)
    stats = stats_service.calculate_run_statistics(session, run_id)

    return templates.TemplateResponse(
        "partials/run_detail_content.html",
        {
            "request": request,
            "run": run,
            "cases": cases,
            "stats": stats,
            "filter": filter
        }
    )


@router.get("/cases/{case_id}/details", response_class=HTMLResponse)
async def get_case_details(
    case_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """HTMX partial for expanding test case details (FR-D3).

    This endpoint loads the full details of a test case including:
    - Test steps with status
    - Error stack trace (if failed)
    - Screenshot (if available)

    Args:
        case_id: ID of the test case.
        request: FastAPI request object.
        session: Database session.

    Returns:
        HTMLResponse: Rendered test case details partial.

    Raises:
        HTTPException: If case not found (404).
    """
    # Get test case with all steps loaded
    case = case_service.get_case_with_steps(session, case_id)

    if not case:
        raise HTTPException(status_code=404, detail=f"Test case {case_id} not found")

    return templates.TemplateResponse(
        "partials/test_step_list.html",
        {
            "request": request,
            "case": case
        }
    )
