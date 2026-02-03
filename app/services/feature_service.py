"""Service layer for Feature operations - async with Beanie."""

from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
import logging

from app.models import Feature, TestCaseDefinition
from app.services.exceptions import FeatureNotFoundError, DeletionConstraintError

logger = logging.getLogger(__name__)


async def create_feature(
    epic_id: str,
    name: str,
    description: Optional[str] = None
) -> Feature:
    """Create a new feature within an epic (FR-N1)."""
    feature = Feature(
        epic_id=PydanticObjectId(epic_id),
        name=name,
        description=description,
        created_at=datetime.utcnow()
    )
    await feature.insert()
    logger.info(f"Feature created with ID: {feature.id} in epic {epic_id}")
    return feature


async def get_feature(feature_id: str) -> Optional[Feature]:
    """Get a feature by ID."""
    return await Feature.get(PydanticObjectId(feature_id))


async def list_features_by_epic(epic_id: str) -> List[Feature]:
    """List all features for an epic ordered by creation time."""
    return await Feature.find(
        Feature.epic_id == PydanticObjectId(epic_id)
    ).sort("-created_at").to_list()


async def update_feature(feature_id: str, **kwargs) -> Feature:
    """Update a feature's fields."""
    feature = await Feature.get(PydanticObjectId(feature_id))
    if not feature:
        raise FeatureNotFoundError(feature_id)
    for key, value in kwargs.items():
        if value is not None:
            setattr(feature, key, value)
    await feature.save()
    logger.info(f"Feature {feature_id} updated")
    return feature


async def delete_feature(feature_id: str) -> None:
    """Delete a feature (FR-N3: with constraint checks)."""
    feature = await Feature.get(PydanticObjectId(feature_id))
    if not feature:
        raise FeatureNotFoundError(feature_id)
    oid = PydanticObjectId(feature_id)
    def_count = await TestCaseDefinition.find(TestCaseDefinition.feature_id == oid).count()
    if def_count > 0:
        raise DeletionConstraintError("Feature", feature_id, "has associated TestCaseDefinitions")
    await feature.delete()
    logger.info(f"Feature {feature_id} deleted")


async def get_test_definition_count(feature_id: str) -> int:
    """Count test definitions for a feature."""
    return await TestCaseDefinition.find(
        TestCaseDefinition.feature_id == PydanticObjectId(feature_id)
    ).count()


async def get_active_test_definition_count(feature_id: str) -> int:
    """Count active test definitions for a feature."""
    return await TestCaseDefinition.find(
        {"feature_id": PydanticObjectId(feature_id), "is_active": True}
    ).count()
