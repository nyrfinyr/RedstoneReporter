"""HTMX partial route handlers for dynamic UI updates (FR-D4)."""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from app.database.session import get_session
from app.services import run_service, case_service

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
