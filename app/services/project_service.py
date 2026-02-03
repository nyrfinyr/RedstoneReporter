"""Service layer for Project operations - async with Beanie."""

from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
import logging

from app.models import Project, Epic, Feature, TestCaseDefinition, TestRun
from app.services.exceptions import ProjectNotFoundError, DeletionConstraintError

logger = logging.getLogger(__name__)


async def create_project(name: str, description: Optional[str] = None) -> Project:
    """Create a new project (FR-E1)."""
    project = Project(name=name, description=description, created_at=datetime.utcnow())
    await project.insert()
    logger.info(f"Project created with ID: {project.id}")
    return project


async def get_project(project_id: str) -> Optional[Project]:
    """Get a project by ID."""
    return await Project.get(PydanticObjectId(project_id))


async def list_projects() -> List[Project]:
    """List all projects ordered by creation time (most recent first)."""
    return await Project.find_all().sort("-created_at").to_list()


async def update_project(project_id: str, **kwargs) -> Project:
    """Update a project's fields."""
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise ProjectNotFoundError(project_id)
    for key, value in kwargs.items():
        if value is not None:
            setattr(project, key, value)
    await project.save()
    logger.info(f"Project {project_id} updated")
    return project


async def delete_project(project_id: str) -> None:
    """Delete a project (FR-E3: with constraint checks)."""
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise ProjectNotFoundError(project_id)
    oid = PydanticObjectId(project_id)
    epic_count = await Epic.find(Epic.project_id == oid).count()
    if epic_count > 0:
        raise DeletionConstraintError("Project", project_id, "has associated Epics")
    run_count = await TestRun.find(TestRun.project_id == oid).count()
    if run_count > 0:
        raise DeletionConstraintError("Project", project_id, "has associated TestRuns")
    await project.delete()
    logger.info(f"Project {project_id} deleted")


async def get_epic_count(project_id: str) -> int:
    """Count epics for a project."""
    return await Epic.find(Epic.project_id == PydanticObjectId(project_id)).count()


async def get_test_definition_count(project_id: str) -> int:
    """Count test definitions across all epics/features of a project."""
    oid = PydanticObjectId(project_id)
    epics = await Epic.find(Epic.project_id == oid).to_list()
    epic_ids = [e.id for e in epics]
    if not epic_ids:
        return 0
    features = await Feature.find({"epic_id": {"$in": epic_ids}}).to_list()
    feature_ids = [f.id for f in features]
    if not feature_ids:
        return 0
    return await TestCaseDefinition.find({"feature_id": {"$in": feature_ids}}).count()


async def get_active_test_definition_count(project_id: str) -> int:
    """Count active test definitions across all epics/features of a project."""
    oid = PydanticObjectId(project_id)
    epics = await Epic.find(Epic.project_id == oid).to_list()
    epic_ids = [e.id for e in epics]
    if not epic_ids:
        return 0
    features = await Feature.find({"epic_id": {"$in": epic_ids}}).to_list()
    feature_ids = [f.id for f in features]
    if not feature_ids:
        return 0
    return await TestCaseDefinition.find(
        {"feature_id": {"$in": feature_ids}, "is_active": True}
    ).count()
