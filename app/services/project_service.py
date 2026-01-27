"""Service layer for Project operations."""

from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List
import logging

from app.models import Project
from app.services.exceptions import ProjectNotFoundError, DeletionConstraintError

logger = logging.getLogger(__name__)


def create_project(session: Session, name: str, description: Optional[str] = None) -> Project:
    """Create a new project (FR-E1).

    Args:
        session: Database session.
        name: Project name (must be unique).
        description: Optional project description.

    Returns:
        Project: The created project with assigned ID.
    """
    project = Project(
        name=name,
        description=description,
        created_at=datetime.utcnow()
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    logger.info(f"Project created with ID: {project.id}")
    return project


def get_project(session: Session, project_id: int) -> Optional[Project]:
    """Get a project by ID.

    Args:
        session: Database session.
        project_id: ID of the project.

    Returns:
        Optional[Project]: The project if found, None otherwise.
    """
    return session.get(Project, project_id)


def list_projects(session: Session) -> List[Project]:
    """List all projects ordered by creation time (most recent first).

    Args:
        session: Database session.

    Returns:
        List[Project]: List of all projects.
    """
    statement = select(Project).order_by(Project.created_at.desc())
    return list(session.exec(statement))


def update_project(session: Session, project_id: int, **kwargs) -> Project:
    """Update a project's fields.

    Args:
        session: Database session.
        project_id: ID of the project to update.
        **kwargs: Fields to update (name, description).

    Returns:
        Project: The updated project.

    Raises:
        ProjectNotFoundError: If project not found.
    """
    project = session.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    for key, value in kwargs.items():
        if value is not None:
            setattr(project, key, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    logger.info(f"Project {project_id} updated")
    return project


def delete_project(session: Session, project_id: int) -> None:
    """Delete a project (FR-E3: with constraint checks).

    Args:
        session: Database session.
        project_id: ID of the project to delete.

    Raises:
        ProjectNotFoundError: If project not found.
        DeletionConstraintError: If project has associated epics or runs.
    """
    project = session.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    if project.epics and len(project.epics) > 0:
        raise DeletionConstraintError("Project", project_id, "has associated Epics")
    if project.runs and len(project.runs) > 0:
        raise DeletionConstraintError("Project", project_id, "has associated TestRuns")

    session.delete(project)
    session.commit()
    logger.info(f"Project {project_id} deleted")
