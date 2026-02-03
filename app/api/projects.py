"""API endpoints for project, epic, and test case definition management."""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import logging

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


async def _build_project_response(project) -> ProjectResponse:
    """Build ProjectResponse with computed counts."""
    pid = str(project.id)
    epic_count = await project_service.get_epic_count(pid)
    test_def_count = await project_service.get_test_definition_count(pid)
    active_def_count = await project_service.get_active_test_definition_count(pid)
    return ProjectResponse(
        id=pid,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        epic_count=epic_count,
        test_definition_count=test_def_count,
        active_test_definition_count=active_def_count
    )


async def _build_epic_response(epic) -> EpicResponse:
    """Build EpicResponse with computed counts."""
    eid = str(epic.id)
    feature_count = await epic_service.get_feature_count(eid)
    test_def_count = await epic_service.get_test_definition_count(eid)
    active_def_count = await epic_service.get_active_test_definition_count(eid)
    return EpicResponse(
        id=eid,
        project_id=str(epic.project_id),
        name=epic.name,
        description=epic.description,
        external_ref=epic.external_ref,
        created_at=epic.created_at,
        feature_count=feature_count,
        test_definition_count=test_def_count,
        active_test_definition_count=active_def_count
    )


# --- Project CRUD ---

@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(request: CreateProjectRequest):
    """Create a new project (FR-E1)."""
    logger.info(f"Creating project: {request.name}")
    project = await project_service.create_project(
        name=request.name, description=request.description
    )
    return await _build_project_response(project)


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects():
    """List all projects (FR-E2)."""
    projects = await project_service.list_projects()
    return [await _build_project_response(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details."""
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return await _build_project_response(project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, request: UpdateProjectRequest):
    """Update a project (FR-E1)."""
    project = await project_service.update_project(
        project_id, name=request.name, description=request.description
    )
    return await _build_project_response(project)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """Delete a project (FR-E3: with constraint check)."""
    await project_service.delete_project(project_id)
    return None


# --- Epic CRUD ---

@router.post("/projects/{project_id}/epics", response_model=EpicResponse, status_code=201)
async def create_epic(project_id: str, request: CreateEpicRequest):
    """Create a new epic within a project (FR-F1)."""
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    logger.info(f"Creating epic: {request.name} in project {project_id}")
    epic = await epic_service.create_epic(
        project_id=project_id,
        name=request.name,
        description=request.description,
        external_ref=request.external_ref
    )
    return await _build_epic_response(epic)


@router.get("/projects/{project_id}/epics", response_model=List[EpicResponse])
async def list_epics(project_id: str):
    """List all epics for a project."""
    epics = await epic_service.list_epics_by_project(project_id)
    return [await _build_epic_response(e) for e in epics]


@router.get("/epics/{epic_id}", response_model=EpicResponse)
async def get_epic(epic_id: str):
    """Get epic details."""
    epic = await epic_service.get_epic(epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail=f"Epic {epic_id} not found")
    return await _build_epic_response(epic)


@router.put("/epics/{epic_id}", response_model=EpicResponse)
async def update_epic(epic_id: str, request: UpdateEpicRequest):
    """Update an epic."""
    epic = await epic_service.update_epic(
        epic_id,
        name=request.name,
        description=request.description,
        external_ref=request.external_ref
    )
    return await _build_epic_response(epic)


@router.delete("/epics/{epic_id}", status_code=204)
async def delete_epic(epic_id: str):
    """Delete an epic (FR-F3: with constraint check — no features allowed)."""
    await epic_service.delete_epic(epic_id)
    return None


# --- TestCaseDefinition read/update/delete (creation moved to features.py) ---

@router.get("/projects/{project_id}/test-cases", response_model=List[TestCaseDefinitionListResponse])
async def list_project_test_cases(
    project_id: str,
    epic_id: Optional[str] = None,
    feature_id: Optional[str] = None,
    priority: Optional[str] = None
):
    """List active test case definitions for a project (FR-H1, FR-H2, FR-P4).

    Used by AI agents to query which tests to execute.
    Supports optional filters: epic_id, feature_id, priority (comma-separated).
    """
    definitions = await definition_service.list_definitions_by_project(
        project_id, epic_id=epic_id, feature_id=feature_id, priority=priority
    )
    results = []
    for d in definitions:
        exec_count = await definition_service.get_execution_count(str(d.id))
        results.append(TestCaseDefinitionListResponse(
            id=str(d.id),
            feature_id=str(d.feature_id),
            title=d.title,
            description=d.description,
            priority=d.priority,
            is_active=d.is_active,
            created_at=d.created_at,
            execution_count=exec_count
        ))
    return results


@router.get("/test-cases/{definition_id}", response_model=TestCaseDefinitionResponse)
async def get_definition(definition_id: str):
    """Get full test case definition details (FR-H3)."""
    definition = await definition_service.get_definition(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail=f"TestCaseDefinition {definition_id} not found")
    exec_count = await definition_service.get_execution_count(definition_id)
    return TestCaseDefinitionResponse(
        id=str(definition.id),
        feature_id=str(definition.feature_id),
        title=definition.title,
        description=definition.description,
        preconditions=definition.preconditions,
        steps=definition.steps,
        expected_result=definition.expected_result,
        priority=definition.priority,
        is_active=definition.is_active,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
        execution_count=exec_count
    )


@router.put("/test-cases/{definition_id}", response_model=TestCaseDefinitionResponse)
async def update_definition(
    definition_id: str,
    request: UpdateTestCaseDefinitionRequest
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

    definition = await definition_service.update_definition(definition_id, **update_data)
    exec_count = await definition_service.get_execution_count(definition_id)
    return TestCaseDefinitionResponse(
        id=str(definition.id),
        feature_id=str(definition.feature_id),
        title=definition.title,
        description=definition.description,
        preconditions=definition.preconditions,
        steps=definition.steps,
        expected_result=definition.expected_result,
        priority=definition.priority,
        is_active=definition.is_active,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
        execution_count=exec_count
    )


@router.delete("/test-cases/{definition_id}", response_model=TestCaseDefinitionResponse)
async def delete_definition(definition_id: str):
    """Soft delete a test case definition (FR-G2): sets is_active=False."""
    definition = await definition_service.soft_delete_definition(definition_id)
    exec_count = await definition_service.get_execution_count(definition_id)
    return TestCaseDefinitionResponse(
        id=str(definition.id),
        feature_id=str(definition.feature_id),
        title=definition.title,
        description=definition.description,
        preconditions=definition.preconditions,
        steps=definition.steps,
        expected_result=definition.expected_result,
        priority=definition.priority,
        is_active=definition.is_active,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
        execution_count=exec_count
    )


@router.delete("/test-cases/{definition_id}/permanent", status_code=204)
async def permanently_delete_definition(definition_id: str):
    """Permanently delete a test case definition from the database."""
    await definition_service.hard_delete_definition(definition_id)
    return None
