"""Service layer for TestCaseDefinition operations."""

from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List
import logging

from app.models import TestCaseDefinition, Feature, Epic
from app.services.exceptions import TestCaseDefinitionNotFoundError

logger = logging.getLogger(__name__)


def create_definition(
    session: Session,
    feature_id: int,
    title: str,
    steps: List[dict],
    description: Optional[str] = None,
    preconditions: Optional[str] = None,
    expected_result: Optional[str] = None,
    priority: str = "medium"
) -> TestCaseDefinition:
    """Create a new test case definition (FR-G1).

    Args:
        session: Database session.
        feature_id: ID of the parent feature.
        title: Test case title.
        steps: List of step dicts [{"description": "...", "order": 0}, ...].
        description: Optional description.
        preconditions: Optional preconditions.
        expected_result: Optional expected result.
        priority: Priority level (critical/high/medium/low).

    Returns:
        TestCaseDefinition: The created definition with assigned ID.
    """
    now = datetime.utcnow()
    definition = TestCaseDefinition(
        feature_id=feature_id,
        title=title,
        steps=steps,
        description=description,
        preconditions=preconditions,
        expected_result=expected_result,
        priority=priority,
        created_at=now,
        updated_at=now
    )
    session.add(definition)
    session.commit()
    session.refresh(definition)
    logger.info(f"TestCaseDefinition created with ID: {definition.id} in feature {feature_id}")
    return definition


def get_definition(session: Session, definition_id: int) -> Optional[TestCaseDefinition]:
    """Get a test case definition by ID.

    Args:
        session: Database session.
        definition_id: ID of the definition.

    Returns:
        Optional[TestCaseDefinition]: The definition if found, None otherwise.
    """
    return session.get(TestCaseDefinition, definition_id)


def list_definitions_by_feature(
    session: Session,
    feature_id: int,
    active_only: bool = True
) -> List[TestCaseDefinition]:
    """List test case definitions for a feature.

    Args:
        session: Database session.
        feature_id: ID of the parent feature.
        active_only: If True, only return active definitions.

    Returns:
        List[TestCaseDefinition]: List of definitions.
    """
    statement = select(TestCaseDefinition).where(TestCaseDefinition.feature_id == feature_id)
    if active_only:
        statement = statement.where(TestCaseDefinition.is_active == True)
    statement = statement.order_by(TestCaseDefinition.created_at.desc())
    return list(session.exec(statement))


def list_definitions_by_project(
    session: Session,
    project_id: int,
    epic_id: Optional[int] = None,
    feature_id: Optional[int] = None,
    priority: Optional[str] = None
) -> List[TestCaseDefinition]:
    """List active definitions across all features of a project (FR-H1, FR-H2).

    Args:
        session: Database session.
        project_id: ID of the project.
        epic_id: Optional filter by specific epic.
        feature_id: Optional filter by specific feature.
        priority: Optional comma-separated priority filter (e.g. "critical,high").

    Returns:
        List[TestCaseDefinition]: List of active definitions.
    """
    statement = (
        select(TestCaseDefinition)
        .join(Feature)
        .join(Epic)
        .where(Epic.project_id == project_id)
        .where(TestCaseDefinition.is_active == True)
    )
    if epic_id:
        statement = statement.where(Feature.epic_id == epic_id)
    if feature_id:
        statement = statement.where(TestCaseDefinition.feature_id == feature_id)
    if priority:
        priorities = [p.strip() for p in priority.split(",")]
        statement = statement.where(TestCaseDefinition.priority.in_(priorities))
    statement = statement.order_by(TestCaseDefinition.created_at.desc())
    return list(session.exec(statement))


def update_definition(session: Session, definition_id: int, **kwargs) -> TestCaseDefinition:
    """Update a test case definition's fields (FR-G2).

    Args:
        session: Database session.
        definition_id: ID of the definition to update.
        **kwargs: Fields to update.

    Returns:
        TestCaseDefinition: The updated definition.

    Raises:
        TestCaseDefinitionNotFoundError: If definition not found.
    """
    definition = session.get(TestCaseDefinition, definition_id)
    if not definition:
        raise TestCaseDefinitionNotFoundError(definition_id)

    for key, value in kwargs.items():
        if value is not None:
            setattr(definition, key, value)

    definition.updated_at = datetime.utcnow()
    session.add(definition)
    session.commit()
    session.refresh(definition)
    logger.info(f"TestCaseDefinition {definition_id} updated")
    return definition


def soft_delete_definition(session: Session, definition_id: int) -> TestCaseDefinition:
    """Soft delete a test case definition (FR-G2): sets is_active=False.

    Args:
        session: Database session.
        definition_id: ID of the definition to deactivate.

    Returns:
        TestCaseDefinition: The deactivated definition.

    Raises:
        TestCaseDefinitionNotFoundError: If definition not found.
    """
    definition = session.get(TestCaseDefinition, definition_id)
    if not definition:
        raise TestCaseDefinitionNotFoundError(definition_id)

    definition.is_active = False
    definition.updated_at = datetime.utcnow()
    session.add(definition)
    session.commit()
    session.refresh(definition)
    logger.info(f"TestCaseDefinition {definition_id} soft-deleted")
    return definition
