"""API endpoints for test run management."""

from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from typing import Optional
import json
import logging

from app.services import run_service, case_service, screenshot_service, stats_service
from app.schemas.run_schemas import StartRunRequest, RunResponse, FinishRunResponse
from app.schemas.case_schemas import (
    ReportTestCaseRequest,
    ReportTestCaseResponse,
    CheckpointResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _build_run_response(run) -> RunResponse:
    """Build RunResponse with computed counts."""
    stats = await stats_service.calculate_run_statistics(str(run.id))
    return RunResponse(
        id=str(run.id),
        name=run.name,
        status=run.status,
        start_time=run.start_time,
        end_time=run.end_time,
        duration=run.duration,
        project_id=str(run.project_id) if run.project_id else None,
        test_count=stats["total_tests"],
        passed_count=stats["passed"],
        failed_count=stats["failed"],
        skipped_count=stats["skipped"]
    )


@router.post("/start", response_model=RunResponse, status_code=201)
async def start_run(request: StartRunRequest):
    """Create a new test run (FR-A1).

    Args:
        request: Start run request with name.

    Returns:
        RunResponse: Created test run information.

    Example:
        POST /api/runs/start
        {"name": "Test Suite 1"}
    """
    logger.info(f"Creating new test run: {request.name}")

    run = await run_service.create_run(request.name, project_id=request.project_id)

    logger.info(f"Test run created with ID: {run.id}")

    return RunResponse(
        id=str(run.id),
        name=run.name,
        status=run.status,
        start_time=run.start_time,
        end_time=run.end_time,
        duration=run.duration,
        project_id=str(run.project_id) if run.project_id else None,
        test_count=0,
        passed_count=0,
        failed_count=0,
        skipped_count=0
    )


@router.post("/{run_id}/report", response_model=ReportTestCaseResponse, status_code=201)
async def report_test_case(
    run_id: str,
    data: str = Form(..., description="JSON string with test case data"),
    screenshot: Optional[UploadFile] = File(None, description="Optional screenshot file")
):
    """Report a single test case with optional screenshot (FR-B1, FR-B2, FR-B3, FR-B4, FR-B5).

    This endpoint accepts multipart/form-data with:
    - data: JSON string containing test case metadata
    - screenshot: Optional image file (PNG/JPEG)

    Args:
        run_id: ID of the test run.
        data: JSON string with test case data.
        screenshot: Optional screenshot file.

    Returns:
        ReportTestCaseResponse: Success status and case ID.
    """
    # Verify run exists
    run = await run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    # Parse JSON metadata
    try:
        case_data = json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in data field: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON in data field: {str(e)}"
        )

    # Validate case_data against schema
    try:
        validated_data = ReportTestCaseRequest(**case_data)
    except Exception as e:
        logger.error(f"Invalid test case data: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid test case data: {str(e)}"
        )

    logger.info(f"Reporting test case '{validated_data.name}' for run {run_id}")

    # Save screenshot if provided (FR-B5)
    screenshot_path = None
    if screenshot:
        # Validate file type
        if screenshot.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid screenshot type: {screenshot.content_type}. Only PNG/JPEG allowed."
            )

        try:
            screenshot_path = await screenshot_service.save_screenshot(
                run_id=run_id,
                case_name=validated_data.name,
                file=screenshot
            )
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            # Continue without screenshot rather than failing the whole request
            screenshot_path = None

    # Create test case with steps (FR-B3)
    try:
        test_case = await case_service.create_test_case(
            run_id=run_id,
            case_data=validated_data.model_dump(),
            screenshot_path=screenshot_path
        )
        logger.info(f"Test case created with ID: {test_case.id}")
    except Exception as e:
        logger.error(f"Failed to create test case: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create test case: {str(e)}"
        )

    return ReportTestCaseResponse(
        success=True,
        case_id=str(test_case.id),
        message=f"Test case '{test_case.name}' reported successfully"
    )


@router.get("/{run_id}/checkpoint", response_model=CheckpointResponse)
async def get_checkpoint(run_id: str):
    """Get list of completed test names for recovery (FR-C1, FR-C2).

    Args:
        run_id: ID of the test run.

    Returns:
        CheckpointResponse: List of completed test case names.
    """
    # Verify run exists
    run = await run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    logger.info(f"Checkpoint query for run {run_id}")

    completed_names = await case_service.get_completed_case_names(run_id)

    logger.info(f"Found {len(completed_names)} completed tests")

    return CheckpointResponse(
        run_id=str(run_id),
        completed_test_names=completed_names,
        total_completed=len(completed_names)
    )


@router.post("/{run_id}/finish", response_model=FinishRunResponse)
async def finish_run(run_id: str):
    """Mark run as completed and calculate final statistics (FR-A3).

    Args:
        run_id: ID of the test run.

    Returns:
        FinishRunResponse: Updated run information with statistics.
    """
    logger.info(f"Finishing test run {run_id}")

    try:
        run = await run_service.finish_run(run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Calculate final statistics
    stats = await stats_service.calculate_run_statistics(run_id)

    logger.info(f"Test run {run_id} completed: {stats['passed']}/{stats['total_tests']} passed")

    return FinishRunResponse(
        id=str(run.id),
        name=run.name,
        status=run.status,
        start_time=run.start_time,
        end_time=run.end_time,
        duration=run.duration,
        total_tests=stats["total_tests"],
        passed=stats["passed"],
        failed=stats["failed"],
        skipped=stats["skipped"],
        success_rate=stats["success_rate"]
    )


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str):
    """Get test run information by ID.

    Args:
        run_id: ID of the test run.

    Returns:
        RunResponse: Test run information.
    """
    run = await run_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Test run {run_id} not found")

    return await _build_run_response(run)
