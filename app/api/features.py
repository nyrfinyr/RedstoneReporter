"""API endpoints for feature management, test case definition creation under features,
and test case (execution) deletion."""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

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


async def _build_feature_response(feature) -> FeatureResponse:
    """Build FeatureResponse with computed counts."""
    fid = str(feature.id)
    test_def_count = await feature_service.get_test_definition_count(fid)
    active_def_count = await feature_service.get_active_test_definition_count(fid)
    return FeatureResponse(
        id=fid,
        epic_id=str(feature.epic_id),
        name=feature.name,
        description=feature.description,
        created_at=feature.created_at,
        test_definition_count=test_def_count,
        active_test_definition_count=active_def_count
    )


# --- Feature CRUD ---

@router.post("/epics/{epic_id}/features", response_model=FeatureResponse, status_code=201)
async def create_feature(epic_id: str, request: CreateFeatureRequest):
    """Create a new feature within an epic (FR-N1)."""
    epic = await epic_service.get_epic(epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail=f"Epic {epic_id} not found")

    logger.info(f"Creating feature: {request.name} in epic {epic_id}")
    feature = await feature_service.create_feature(
        epic_id=epic_id,
        name=request.name,
        description=request.description
    )
    return await _build_feature_response(feature)


@router.get("/epics/{epic_id}/features", response_model=List[FeatureResponse])
async def list_features(epic_id: str):
    """List all features for an epic."""
    features = await feature_service.list_features_by_epic(epic_id)
    return [await _build_feature_response(f) for f in features]


@router.get("/features/{feature_id}", response_model=FeatureResponse)
async def get_feature(feature_id: str):
    """Get feature details."""
    feature = await feature_service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")
    return await _build_feature_response(feature)


@router.put("/features/{feature_id}", response_model=FeatureResponse)
async def update_feature(feature_id: str, request: UpdateFeatureRequest):
    """Update a feature."""
    feature = await feature_service.update_feature(
        feature_id, name=request.name, description=request.description
    )
    return await _build_feature_response(feature)


@router.delete("/features/{feature_id}", status_code=204)
async def delete_feature(feature_id: str):
    """Delete a feature (FR-N3: with constraint check)."""
    await feature_service.delete_feature(feature_id)
    return None


# --- TestCaseDefinition creation under Feature ---

@router.post("/features/{feature_id}/test-cases", response_model=TestCaseDefinitionResponse, status_code=201)
async def create_definition(feature_id: str, request: CreateTestCaseDefinitionRequest):
    """Create a new test case definition within a feature (FR-P3)."""
    feature = await feature_service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

    logger.info(f"Creating test case definition: {request.title} in feature {feature_id}")
    steps_data = [s.model_dump() for s in request.steps]
    definition = await definition_service.create_definition(
        feature_id=feature_id,
        title=request.title,
        steps=steps_data,
        description=request.description,
        preconditions=request.preconditions,
        expected_result=request.expected_result,
        priority=request.priority
    )
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
        execution_count=0
    )


# --- Test Case (execution) deletion ---

@router.delete("/cases/{case_id}", status_code=204)
async def delete_test_case(case_id: str):
    """Permanently delete a test case execution (FR-O1, FR-O3)."""
    await case_service.delete_test_case(case_id)
    return None
