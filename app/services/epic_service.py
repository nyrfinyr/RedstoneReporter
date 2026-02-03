"""Service layer for Epic operations - async with Beanie."""

from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
import logging

from app.models import Epic, Feature, TestCaseDefinition
from app.services.exceptions import EpicNotFoundError, DeletionConstraintError

logger = logging.getLogger(__name__)


async def create_epic(
    project_id: str,
    name: str,
    description: Optional[str] = None,
    external_ref: Optional[str] = None
) -> Epic:
    """Create a new epic within a project (FR-F1)."""
    epic = Epic(
        project_id=PydanticObjectId(project_id),
        name=name,
        description=description,
        external_ref=external_ref,
        created_at=datetime.utcnow()
    )
    await epic.insert()
    logger.info(f"Epic created with ID: {epic.id} in project {project_id}")
    return epic


async def get_epic(epic_id: str) -> Optional[Epic]:
    """Get an epic by ID."""
    return await Epic.get(PydanticObjectId(epic_id))


async def list_epics_by_project(project_id: str) -> List[Epic]:
    """List all epics for a project ordered by creation time."""
    return await Epic.find(
        Epic.project_id == PydanticObjectId(project_id)
    ).sort("-created_at").to_list()


async def update_epic(epic_id: str, **kwargs) -> Epic:
    """Update an epic's fields."""
    epic = await Epic.get(PydanticObjectId(epic_id))
    if not epic:
        raise EpicNotFoundError(epic_id)
    for key, value in kwargs.items():
        if value is not None:
            setattr(epic, key, value)
    await epic.save()
    logger.info(f"Epic {epic_id} updated")
    return epic


async def delete_epic(epic_id: str) -> None:
    """Delete an epic (FR-F3: with constraint checks)."""
    epic = await Epic.get(PydanticObjectId(epic_id))
    if not epic:
        raise EpicNotFoundError(epic_id)
    oid = PydanticObjectId(epic_id)
    feature_count = await Feature.find(Feature.epic_id == oid).count()
    if feature_count > 0:
        raise DeletionConstraintError("Epic", epic_id, "has associated Features")
    await epic.delete()
    logger.info(f"Epic {epic_id} deleted")


async def get_feature_count(epic_id: str) -> int:
    """Count features for an epic."""
    return await Feature.find(Feature.epic_id == PydanticObjectId(epic_id)).count()


async def get_test_definition_count(epic_id: str) -> int:
    """Count test definitions across all features of an epic."""
    oid = PydanticObjectId(epic_id)
    features = await Feature.find(Feature.epic_id == oid).to_list()
    feature_ids = [f.id for f in features]
    if not feature_ids:
        return 0
    return await TestCaseDefinition.find({"feature_id": {"$in": feature_ids}}).count()


async def get_active_test_definition_count(epic_id: str) -> int:
    """Count active test definitions across all features of an epic."""
    oid = PydanticObjectId(epic_id)
    features = await Feature.find(Feature.epic_id == oid).to_list()
    feature_ids = [f.id for f in features]
    if not feature_ids:
        return 0
    return await TestCaseDefinition.find(
        {"feature_id": {"$in": feature_ids}, "is_active": True}
    ).count()
