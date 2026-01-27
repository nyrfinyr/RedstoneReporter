"""API endpoints for feature management, test case definition creation under features,
and test case (execution) deletion."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
import logging

from app.database.session import get_session
from app.services import epic_service, feature_service, definition_service, case_service
from app.schemas.feature_schemas import (
    CreateFeatureRequest, UpdateFeatureRequest, FeatureResponse
)
from app.schemas.definition_schemas import (
    CreateTestCaseDefinitionRequest,
    TestCaseDefinitionResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Feature CRUD ---

@router.post("/epics/{epic_id}/features", response_model=FeatureResponse, status_code=201)
async def create_feature(
    epic_id: int,
    request: CreateFeatureRequest,
    session: Session = Depends(get_session)
):
    """Create a new feature within an epic (FR-N1)."""
    epic = epic_service.get_epic(session, epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail=f"Epic {epic_id} not found")

    logger.info(f"Creating feature: {request.name} in epic {epic_id}")
    feature = feature_service.create_feature(
        session,
        epic_id=epic_id,
        name=request.name,
        description=request.description
    )
    return FeatureResponse(
        id=feature.id,
        epic_id=feature.epic_id,
        name=feature.name,
        description=feature.description,
        created_at=feature.created_at,
        test_definition_count=feature.test_definition_count,
        active_test_definition_count=feature.active_test_definition_count
    )


@router.get("/epics/{epic_id}/features", response_model=List[FeatureResponse])
async def list_features(epic_id: int, session: Session = Depends(get_session)):
    """List all features for an epic."""
    features = feature_service.list_features_by_epic(session, epic_id)
    return [
        FeatureResponse(
            id=f.id,
            epic_id=f.epic_id,
            name=f.name,
            description=f.description,
            created_at=f.created_at,
            test_definition_count=f.test_definition_count,
            active_test_definition_count=f.active_test_definition_count
        )
        for f in features
    ]


@router.get("/features/{feature_id}", response_model=FeatureResponse)
async def get_feature(feature_id: int, session: Session = Depends(get_session)):
    """Get feature details."""
    feature = feature_service.get_feature(session, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")
    return FeatureResponse(
        id=feature.id,
        epic_id=feature.epic_id,
        name=feature.name,
        description=feature.description,
        created_at=feature.created_at,
        test_definition_count=feature.test_definition_count,
        active_test_definition_count=feature.active_test_definition_count
    )


@router.put("/features/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: int,
    request: UpdateFeatureRequest,
    session: Session = Depends(get_session)
):
    """Update a feature."""
    feature = feature_service.update_feature(
        session, feature_id,
        name=request.name,
        description=request.description
    )
    return FeatureResponse(
        id=feature.id,
        epic_id=feature.epic_id,
        name=feature.name,
        description=feature.description,
        created_at=feature.created_at,
        test_definition_count=feature.test_definition_count,
        active_test_definition_count=feature.active_test_definition_count
    )


@router.delete("/features/{feature_id}", status_code=204)
async def delete_feature(feature_id: int, session: Session = Depends(get_session)):
    """Delete a feature (FR-N3: with constraint check)."""
    feature_service.delete_feature(session, feature_id)
    return None


# --- TestCaseDefinition creation under Feature ---

@router.post("/features/{feature_id}/test-cases", response_model=TestCaseDefinitionResponse, status_code=201)
async def create_definition(
    feature_id: int,
    request: CreateTestCaseDefinitionRequest,
    session: Session = Depends(get_session)
):
    """Create a new test case definition within a feature (FR-P3)."""
    feature = feature_service.get_feature(session, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

    logger.info(f"Creating test case definition: {request.title} in feature {feature_id}")
    steps_data = [s.model_dump() for s in request.steps]
    definition = definition_service.create_definition(
        session,
        feature_id=feature_id,
        title=request.title,
        steps=steps_data,
        description=request.description,
        preconditions=request.preconditions,
        expected_result=request.expected_result,
        priority=request.priority
    )
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


# --- Test Case (execution) deletion ---

@router.delete("/cases/{case_id}", status_code=204)
async def delete_test_case(case_id: int, session: Session = Depends(get_session)):
    """Permanently delete a test case execution (FR-O1, FR-O3)."""
    case_service.delete_test_case(session, case_id)
    return None
