"""Web UI route handlers for projects, epics, features, and test case definitions."""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from app.database.session import get_session
from app.services import project_service, epic_service, feature_service, definition_service

templates = Jinja2Templates(directory=str(Path("app/templates")))

router = APIRouter()


@router.get("/projects", response_class=HTMLResponse)
async def projects_list(
    request: Request,
    session: Session = Depends(get_session)
):
    """Projects list page (FR-E2)."""
    projects = project_service.list_projects(session)
    return templates.TemplateResponse(
        "projects_list.html",
        {"request": request, "projects": projects}
    )


@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(
    project_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Project detail page with epics (FR-UI2)."""
    project = project_service.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    epics = epic_service.list_epics_by_project(session, project_id)
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "project": project, "epics": epics}
    )


@router.get("/projects/{project_id}/epics/{epic_id}", response_class=HTMLResponse)
async def epic_detail(
    project_id: int,
    epic_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Epic detail page with features (FR-UI3)."""
    project = project_service.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    epic = epic_service.get_epic(session, epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail=f"Epic {epic_id} not found")
    features = feature_service.list_features_by_epic(session, epic_id)
    return templates.TemplateResponse(
        "epic_detail.html",
        {"request": request, "project": project, "epic": epic, "features": features}
    )


@router.get("/features/{feature_id}", response_class=HTMLResponse)
async def feature_detail(
    feature_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Feature detail page with test case definitions."""
    feature = feature_service.get_feature(session, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")
    epic = epic_service.get_epic(session, feature.epic_id)
    project = project_service.get_project(session, epic.project_id)
    definitions = definition_service.list_definitions_by_feature(session, feature_id, active_only=False)
    return templates.TemplateResponse(
        "feature_detail.html",
        {
            "request": request,
            "project": project,
            "epic": epic,
            "feature": feature,
            "definitions": definitions
        }
    )


@router.get("/features/{feature_id}/test-cases/new", response_class=HTMLResponse)
async def new_definition_form(
    feature_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Form for creating a new test case definition (FR-G1)."""
    feature = feature_service.get_feature(session, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")
    epic = epic_service.get_epic(session, feature.epic_id)
    project = project_service.get_project(session, epic.project_id)
    return templates.TemplateResponse(
        "definition_form.html",
        {
            "request": request,
            "project": project,
            "epic": epic,
            "feature": feature,
            "definition": None
        }
    )


@router.get("/test-cases/{definition_id}/edit", response_class=HTMLResponse)
async def edit_definition_form(
    definition_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Form for editing an existing test case definition (FR-G2)."""
    definition = definition_service.get_definition(session, definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail=f"TestCaseDefinition {definition_id} not found")
    feature = feature_service.get_feature(session, definition.feature_id)
    epic = epic_service.get_epic(session, feature.epic_id)
    project = project_service.get_project(session, epic.project_id)
    return templates.TemplateResponse(
        "definition_form.html",
        {
            "request": request,
            "project": project,
            "epic": epic,
            "feature": feature,
            "definition": definition
        }
    )


@router.get("/test-cases/{definition_id}", response_class=HTMLResponse)
async def definition_detail(
    definition_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Test case definition detail page (FR-G4)."""
    definition = definition_service.get_definition(session, definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail=f"TestCaseDefinition {definition_id} not found")
    feature = feature_service.get_feature(session, definition.feature_id)
    epic = epic_service.get_epic(session, feature.epic_id)
    project = project_service.get_project(session, epic.project_id)
    executions = definition.executions if definition.executions else []
    return templates.TemplateResponse(
        "definition_detail.html",
        {
            "request": request,
            "project": project,
            "epic": epic,
            "feature": feature,
            "definition": definition,
            "executions": executions
        }
    )
