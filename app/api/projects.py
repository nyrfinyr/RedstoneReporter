"""API endpoints for project, epic, and test case definition management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional, List
import logging

from app.database.session import get_session
from app.services import project_service, epic_service, definition_service
from app.schemas.project_schemas import (
    CreateProjectRequest, UpdateProjectRequest, ProjectResponse
)
from app.schemas.epic_schemas import (
    CreateEpicRequest, UpdateEpicRequest, EpicResponse
)
from app.schemas.definition_schemas import (
    UpdateTestCaseDefinitionRequest,
    TestCaseDefinitionResponse,
    TestCaseDefinitionListResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Project CRUD ---

@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: CreateProjectRequest,
    session: Session = Depends(get_session)
):
    """Create a new project (FR-E1)."""
    logger.info(f"Creating project: {request.name}")
    project = project_service.create_project(
        session, name=request.name, description=request.description
    )
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        epic_count=project.epic_count,
        test_definition_count=project.test_definition_count,
        active_test_definition_count=project.active_test_definition_count
    )


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(session: Session = Depends(get_session)):
    """List all projects (FR-E2)."""
    projects = project_service.list_projects(session)
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            created_at=p.created_at,
            epic_count=p.epic_count,
            test_definition_count=p.test_definition_count,
            active_test_definition_count=p.active_test_definition_count
        )
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, session: Session = Depends(get_session)):
    """Get project details."""
    project = project_service.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        epic_count=project.epic_count,
        test_definition_count=project.test_definition_count,
        active_test_definition_count=project.active_test_definition_count
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: UpdateProjectRequest,
    session: Session = Depends(get_session)
):
    """Update a project (FR-E1)."""
    project = project_service.update_project(
        session, project_id,
        name=request.name,
        description=request.description
    )
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        epic_count=project.epic_count,
        test_definition_count=project.test_definition_count,
        active_test_definition_count=project.active_test_definition_count
    )


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, session: Session = Depends(get_session)):
    """Delete a project (FR-E3: with constraint check)."""
    project_service.delete_project(session, project_id)
    return None


# --- Epic CRUD ---

@router.post("/projects/{project_id}/epics", response_model=EpicResponse, status_code=201)
async def create_epic(
    project_id: int,
    request: CreateEpicRequest,
    session: Session = Depends(get_session)
):
    """Create a new epic within a project (FR-F1)."""
    project = project_service.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    logger.info(f"Creating epic: {request.name} in project {project_id}")
    epic = epic_service.create_epic(
        session,
        project_id=project_id,
        name=request.name,
        description=request.description,
        external_ref=request.external_ref
    )
    return EpicResponse(
        id=epic.id,
        project_id=epic.project_id,
        name=epic.name,
        description=epic.description,
        external_ref=epic.external_ref,
        created_at=epic.created_at,
        feature_count=epic.feature_count,
        test_definition_count=epic.test_definition_count,
        active_test_definition_count=epic.active_test_definition_count
    )


@router.get("/projects/{project_id}/epics", response_model=List[EpicResponse])
async def list_epics(project_id: int, session: Session = Depends(get_session)):
    """List all epics for a project."""
    epics = epic_service.list_epics_by_project(session, project_id)
    return [
        EpicResponse(
            id=e.id,
            project_id=e.project_id,
            name=e.name,
            description=e.description,
            external_ref=e.external_ref,
            created_at=e.created_at,
            feature_count=e.feature_count,
            test_definition_count=e.test_definition_count,
            active_test_definition_count=e.active_test_definition_count
        )
        for e in epics
    ]


@router.get("/epics/{epic_id}", response_model=EpicResponse)
async def get_epic(epic_id: int, session: Session = Depends(get_session)):
    """Get epic details."""
    epic = epic_service.get_epic(session, epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail=f"Epic {epic_id} not found")
    return EpicResponse(
        id=epic.id,
        project_id=epic.project_id,
        name=epic.name,
        description=epic.description,
        external_ref=epic.external_ref,
        created_at=epic.created_at,
        feature_count=epic.feature_count,
        test_definition_count=epic.test_definition_count,
        active_test_definition_count=epic.active_test_definition_count
    )


@router.put("/epics/{epic_id}", response_model=EpicResponse)
async def update_epic(
    epic_id: int,
    request: UpdateEpicRequest,
    session: Session = Depends(get_session)
):
    """Update an epic."""
    epic = epic_service.update_epic(
        session, epic_id,
        name=request.name,
        description=request.description,
        external_ref=request.external_ref
    )
    return EpicResponse(
        id=epic.id,
        project_id=epic.project_id,
        name=epic.name,
        description=epic.description,
        external_ref=epic.external_ref,
        created_at=epic.created_at,
        feature_count=epic.feature_count,
        test_definition_count=epic.test_definition_count,
        active_test_definition_count=epic.active_test_definition_count
    )


@router.delete("/epics/{epic_id}", status_code=204)
async def delete_epic(epic_id: int, session: Session = Depends(get_session)):
    """Delete an epic (FR-F3: with constraint check — no features allowed)."""
    epic_service.delete_epic(session, epic_id)
    return None


# --- TestCaseDefinition read/update/delete (creation moved to features.py) ---

@router.get("/projects/{project_id}/test-cases", response_model=List[TestCaseDefinitionListResponse])
async def list_project_test_cases(
    project_id: int,
    epic_id: Optional[int] = None,
    feature_id: Optional[int] = None,
    priority: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List active test case definitions for a project (FR-H1, FR-H2, FR-P4).

    Used by AI agents to query which tests to execute.
    Supports optional filters: epic_id, feature_id, priority (comma-separated).
    """
    definitions = definition_service.list_definitions_by_project(
        session, project_id, epic_id=epic_id, feature_id=feature_id, priority=priority
    )
    return [
        TestCaseDefinitionListResponse(
            id=d.id,
            feature_id=d.feature_id,
            title=d.title,
            description=d.description,
            priority=d.priority,
            is_active=d.is_active,
            created_at=d.created_at,
            execution_count=d.execution_count
        )
        for d in definitions
    ]


@router.get("/test-cases/{definition_id}", response_model=TestCaseDefinitionResponse)
async def get_definition(definition_id: int, session: Session = Depends(get_session)):
    """Get full test case definition details (FR-H3)."""
    definition = definition_service.get_definition(session, definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail=f"TestCaseDefinition {definition_id} not found")
    return TestCaseDefinitionResponse(
        id=definition.id,
        feature_id=definition.feature_id,
        title=definition.title,
        description=definition.description,
        preconditions=definition.preconditions,
        steps=definition.steps,
        expected_result=definition.expected_result,
        priority=definition.priority,
        is_active=definition.is_active,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
        execution_count=definition.execution_count
    )


@router.put("/test-cases/{definition_id}", response_model=TestCaseDefinitionResponse)
async def update_definition(
    definition_id: int,
    request: UpdateTestCaseDefinitionRequest,
    session: Session = Depends(get_session)
):
    """Update a test case definition (FR-G2)."""
    update_data = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.description is not None:
        update_data["description"] = request.description
    if request.preconditions is not None:
        update_data["preconditions"] = request.preconditions
    if request.steps is not None:
        update_data["steps"] = [s.model_dump() for s in request.steps]
    if request.expected_result is not None:
        update_data["expected_result"] = request.expected_result
    if request.priority is not None:
        update_data["priority"] = request.priority
    if request.is_active is not None:
        update_data["is_active"] = request.is_active

    definition = definition_service.update_definition(session, definition_id, **update_data)
    return TestCaseDefinitionResponse(
        id=definition.id,
        feature_id=definition.feature_id,
        title=definition.title,
        description=definition.description,
        preconditions=definition.preconditions,
        steps=definition.steps,
        expected_result=definition.expected_result,
        priority=definition.priority,
        is_active=definition.is_active,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
        execution_count=definition.execution_count
    )


@router.delete("/test-cases/{definition_id}", response_model=TestCaseDefinitionResponse)
async def delete_definition(definition_id: int, session: Session = Depends(get_session)):
    """Soft delete a test case definition (FR-G2): sets is_active=False."""
    definition = definition_service.soft_delete_definition(session, definition_id)
    return TestCaseDefinitionResponse(
        id=definition.id,
        feature_id=definition.feature_id,
        title=definition.title,
        description=definition.description,
        preconditions=definition.preconditions,
        steps=definition.steps,
        expected_result=definition.expected_result,
        priority=definition.priority,
        is_active=definition.is_active,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
        execution_count=definition.execution_count
    )
