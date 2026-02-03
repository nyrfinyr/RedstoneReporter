"""Service layer for TestCaseDefinition operations - async with Beanie."""

from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
import logging

from app.models import TestCaseDefinition, Feature, Epic, TestCase
from app.services.exceptions import TestCaseDefinitionNotFoundError

logger = logging.getLogger(__name__)


async def create_definition(
    feature_id: str,
    title: str,
    steps: List[dict],
    description: Optional[str] = None,
    preconditions: Optional[str] = None,
    expected_result: Optional[str] = None,
    priority: str = "medium"
) -> TestCaseDefinition:
    """Create a new test case definition (FR-G1)."""
    now = datetime.utcnow()
    definition = TestCaseDefinition(
        feature_id=PydanticObjectId(feature_id),
        title=title,
        steps=steps,
        description=description,
        preconditions=preconditions,
        expected_result=expected_result,
        priority=priority,
        created_at=now,
        updated_at=now
    )
    await definition.insert()
    logger.info(f"TestCaseDefinition created with ID: {definition.id} in feature {feature_id}")
    return definition


async def get_definition(definition_id: str) -> Optional[TestCaseDefinition]:
    """Get a test case definition by ID."""
    return await TestCaseDefinition.get(PydanticObjectId(definition_id))


async def list_definitions_by_feature(
    feature_id: str,
    active_only: bool = True
) -> List[TestCaseDefinition]:
    """List test case definitions for a feature."""
    query = {"feature_id": PydanticObjectId(feature_id)}
    if active_only:
        query["is_active"] = True
    return await TestCaseDefinition.find(query).sort("-created_at").to_list()


async def list_definitions_by_project(
    project_id: str,
    epic_id: Optional[str] = None,
    feature_id: Optional[str] = None,
    priority: Optional[str] = None
) -> List[TestCaseDefinition]:
    """List active definitions across all features of a project (FR-H1, FR-H2)."""
    if feature_id:
        query_filter = {"feature_id": PydanticObjectId(feature_id), "is_active": True}
    elif epic_id:
        features = await Feature.find(Feature.epic_id == PydanticObjectId(epic_id)).to_list()
        fids = [f.id for f in features]
        query_filter = {"feature_id": {"$in": fids}, "is_active": True}
    else:
        epics = await Epic.find(Epic.project_id == PydanticObjectId(project_id)).to_list()
        eids = [e.id for e in epics]
        features = await Feature.find({"epic_id": {"$in": eids}}).to_list()
        fids = [f.id for f in features]
        query_filter = {"feature_id": {"$in": fids}, "is_active": True}

    if priority:
        priorities = [p.strip() for p in priority.split(",")]
        query_filter["priority"] = {"$in": priorities}

    return await TestCaseDefinition.find(query_filter).sort("-created_at").to_list()


async def update_definition(definition_id: str, **kwargs) -> TestCaseDefinition:
    """Update a test case definition's fields (FR-G2)."""
    definition = await TestCaseDefinition.get(PydanticObjectId(definition_id))
    if not definition:
        raise TestCaseDefinitionNotFoundError(definition_id)

    for key, value in kwargs.items():
        if value is not None:
            setattr(definition, key, value)

    definition.updated_at = datetime.utcnow()
    await definition.save()
    logger.info(f"TestCaseDefinition {definition_id} updated")
    return definition


async def soft_delete_definition(definition_id: str) -> TestCaseDefinition:
    """Soft delete a test case definition: sets is_active=False."""
    definition = await TestCaseDefinition.get(PydanticObjectId(definition_id))
    if not definition:
        raise TestCaseDefinitionNotFoundError(definition_id)

    definition.is_active = False
    definition.updated_at = datetime.utcnow()
    await definition.save()
    logger.info(f"TestCaseDefinition {definition_id} soft-deleted")
    return definition


async def hard_delete_definition(definition_id: str) -> None:
    """Permanently delete a test case definition from the database."""
    definition = await TestCaseDefinition.get(PydanticObjectId(definition_id))
    if not definition:
        raise TestCaseDefinitionNotFoundError(definition_id)

    await definition.delete()
    logger.info(f"TestCaseDefinition {definition_id} permanently deleted")


async def get_execution_count(definition_id: str) -> int:
    """Count test case executions linked to a definition."""
    return await TestCase.find(
        TestCase.definition_id == PydanticObjectId(definition_id)
    ).count()
