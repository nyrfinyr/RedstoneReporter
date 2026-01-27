"""Service layer for Feature operations."""

from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List
import logging

from app.models import Feature
from app.services.exceptions import FeatureNotFoundError, DeletionConstraintError

logger = logging.getLogger(__name__)


def create_feature(
    session: Session,
    epic_id: int,
    name: str,
    description: Optional[str] = None
) -> Feature:
    """Create a new feature within an epic (FR-N1).

    Args:
        session: Database session.
        epic_id: ID of the parent epic.
        name: Feature name.
        description: Optional description.

    Returns:
        Feature: The created feature with assigned ID.
    """
    feature = Feature(
        epic_id=epic_id,
        name=name,
        description=description,
        created_at=datetime.utcnow()
    )
    session.add(feature)
    session.commit()
    session.refresh(feature)
    logger.info(f"Feature created with ID: {feature.id} in epic {epic_id}")
    return feature


def get_feature(session: Session, feature_id: int) -> Optional[Feature]:
    """Get a feature by ID.

    Args:
        session: Database session.
        feature_id: ID of the feature.

    Returns:
        Optional[Feature]: The feature if found, None otherwise.
    """
    return session.get(Feature, feature_id)


def list_features_by_epic(session: Session, epic_id: int) -> List[Feature]:
    """List all features for an epic ordered by creation time.

    Args:
        session: Database session.
        epic_id: ID of the parent epic.

    Returns:
        List[Feature]: List of features in the epic.
    """
    statement = (
        select(Feature)
        .where(Feature.epic_id == epic_id)
        .order_by(Feature.created_at.desc())
    )
    return list(session.exec(statement))


def update_feature(session: Session, feature_id: int, **kwargs) -> Feature:
    """Update a feature's fields.

    Args:
        session: Database session.
        feature_id: ID of the feature to update.
        **kwargs: Fields to update (name, description).

    Returns:
        Feature: The updated feature.

    Raises:
        FeatureNotFoundError: If feature not found.
    """
    feature = session.get(Feature, feature_id)
    if not feature:
        raise FeatureNotFoundError(feature_id)

    for key, value in kwargs.items():
        if value is not None:
            setattr(feature, key, value)

    session.add(feature)
    session.commit()
    session.refresh(feature)
    logger.info(f"Feature {feature_id} updated")
    return feature


def delete_feature(session: Session, feature_id: int) -> None:
    """Delete a feature (FR-N3: with constraint checks).

    Args:
        session: Database session.
        feature_id: ID of the feature to delete.

    Raises:
        FeatureNotFoundError: If feature not found.
        DeletionConstraintError: If feature has associated test case definitions.
    """
    feature = session.get(Feature, feature_id)
    if not feature:
        raise FeatureNotFoundError(feature_id)

    if feature.test_case_definitions and len(feature.test_case_definitions) > 0:
        raise DeletionConstraintError("Feature", feature_id, "has associated TestCaseDefinitions")

    session.delete(feature)
    session.commit()
    logger.info(f"Feature {feature_id} deleted")
