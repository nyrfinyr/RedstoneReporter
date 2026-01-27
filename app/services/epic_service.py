"""Service layer for Epic operations."""

from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List
import logging

from app.models import Epic
from app.services.exceptions import EpicNotFoundError, DeletionConstraintError

logger = logging.getLogger(__name__)


def create_epic(
    session: Session,
    project_id: int,
    name: str,
    description: Optional[str] = None,
    external_ref: Optional[str] = None
) -> Epic:
    """Create a new epic within a project (FR-F1).

    Args:
        session: Database session.
        project_id: ID of the parent project.
        name: Epic name.
        description: Optional description.
        external_ref: Optional external reference (e.g. Jira ID).

    Returns:
        Epic: The created epic with assigned ID.
    """
    epic = Epic(
        project_id=project_id,
        name=name,
        description=description,
        external_ref=external_ref,
        created_at=datetime.utcnow()
    )
    session.add(epic)
    session.commit()
    session.refresh(epic)
    logger.info(f"Epic created with ID: {epic.id} in project {project_id}")
    return epic


def get_epic(session: Session, epic_id: int) -> Optional[Epic]:
    """Get an epic by ID.

    Args:
        session: Database session.
        epic_id: ID of the epic.

    Returns:
        Optional[Epic]: The epic if found, None otherwise.
    """
    return session.get(Epic, epic_id)


def list_epics_by_project(session: Session, project_id: int) -> List[Epic]:
    """List all epics for a project ordered by creation time.

    Args:
        session: Database session.
        project_id: ID of the parent project.

    Returns:
        List[Epic]: List of epics in the project.
    """
    statement = (
        select(Epic)
        .where(Epic.project_id == project_id)
        .order_by(Epic.created_at.desc())
    )
    return list(session.exec(statement))


def update_epic(session: Session, epic_id: int, **kwargs) -> Epic:
    """Update an epic's fields.

    Args:
        session: Database session.
        epic_id: ID of the epic to update.
        **kwargs: Fields to update (name, description, external_ref).

    Returns:
        Epic: The updated epic.

    Raises:
        EpicNotFoundError: If epic not found.
    """
    epic = session.get(Epic, epic_id)
    if not epic:
        raise EpicNotFoundError(epic_id)

    for key, value in kwargs.items():
        if value is not None:
            setattr(epic, key, value)

    session.add(epic)
    session.commit()
    session.refresh(epic)
    logger.info(f"Epic {epic_id} updated")
    return epic


def delete_epic(session: Session, epic_id: int) -> None:
    """Delete an epic (FR-F3: with constraint checks).

    Args:
        session: Database session.
        epic_id: ID of the epic to delete.

    Raises:
        EpicNotFoundError: If epic not found.
        DeletionConstraintError: If epic has associated test case definitions.
    """
    epic = session.get(Epic, epic_id)
    if not epic:
        raise EpicNotFoundError(epic_id)

    if epic.test_case_definitions and len(epic.test_case_definitions) > 0:
        raise DeletionConstraintError("Epic", epic_id, "has associated TestCaseDefinitions")

    session.delete(epic)
    session.commit()
    logger.info(f"Epic {epic_id} deleted")
