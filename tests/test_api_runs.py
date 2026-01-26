"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
import json


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "RedstoneReporter"


def test_start_run(client: TestClient):
    """Test starting a new test run (FR-A1)."""
    response = client.post(
        "/api/runs/start",
        json={"name": "Test Suite 1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Suite 1"
    assert data["status"] == "running"
    assert "id" in data
    assert data["id"] > 0


def test_get_run(client: TestClient):
    """Test getting run information."""
    # Create a run first
    create_response = client.post(
        "/api/runs/start",
        json={"name": "Test Suite 2"}
    )
    run_id = create_response.json()["id"]

    # Get the run
    response = client.get(f"/api/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run_id
    assert data["name"] == "Test Suite 2"


def test_get_run_not_found(client: TestClient):
    """Test getting non-existent run returns 404."""
    response = client.get("/api/runs/9999")
    assert response.status_code == 404


def test_report_test_case(client: TestClient):
    """Test reporting a test case (FR-B1)."""
    # Create a run first
    create_response = client.post(
        "/api/runs/start",
        json={"name": "Test Suite 3"}
    )
    run_id = create_response.json()["id"]

    # Report a test case
    case_data = {
        "name": "Login Test",
        "status": "passed",
        "duration": 1500,
        "steps": [
            {"description": "Open page", "status": "passed"},
            {"description": "Enter credentials", "status": "passed"}
        ]
    }

    response = client.post(
        f"/api/runs/{run_id}/report",
        data={"data": json.dumps(case_data)}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "case_id" in data


def test_checkpoint_query(client: TestClient):
    """Test checkpoint query for recovery (FR-C1)."""
    # Create a run
    create_response = client.post(
        "/api/runs/start",
        json={"name": "Test Suite 4"}
    )
    run_id = create_response.json()["id"]

    # Report two test cases
    for i in range(2):
        case_data = {
            "name": f"Test {i+1}",
            "status": "passed",
            "duration": 1000,
            "steps": []
        }
        client.post(
            f"/api/runs/{run_id}/report",
            data={"data": json.dumps(case_data)}
        )

    # Query checkpoint
    response = client.get(f"/api/runs/{run_id}/checkpoint")
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == run_id
    assert len(data["completed_test_names"]) == 2
    assert "Test 1" in data["completed_test_names"]
    assert "Test 2" in data["completed_test_names"]


def test_finish_run(client: TestClient):
    """Test finishing a run (FR-A3)."""
    # Create a run
    create_response = client.post(
        "/api/runs/start",
        json={"name": "Test Suite 5"}
    )
    run_id = create_response.json()["id"]

    # Finish the run
    response = client.post(f"/api/runs/{run_id}/finish")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["end_time"] is not None


def test_full_workflow(client: TestClient):
    """Test complete workflow: start → report → checkpoint → finish."""
    # 1. Start run
    start_response = client.post(
        "/api/runs/start",
        json={"name": "Complete Workflow Test"}
    )
    assert start_response.status_code == 201
    run_id = start_response.json()["id"]

    # 2. Report passed test
    passed_case = {
        "name": "Passed Test",
        "status": "passed",
        "duration": 1200,
        "steps": [{"description": "Step 1", "status": "passed"}]
    }
    report1 = client.post(
        f"/api/runs/{run_id}/report",
        data={"data": json.dumps(passed_case)}
    )
    assert report1.status_code == 201

    # 3. Report failed test
    failed_case = {
        "name": "Failed Test",
        "status": "failed",
        "duration": 800,
        "error_message": "Element not found",
        "steps": [{"description": "Step 1", "status": "failed"}]
    }
    report2 = client.post(
        f"/api/runs/{run_id}/report",
        data={"data": json.dumps(failed_case)}
    )
    assert report2.status_code == 201

    # 4. Query checkpoint
    checkpoint = client.get(f"/api/runs/{run_id}/checkpoint")
    assert checkpoint.status_code == 200
    assert checkpoint.json()["total_completed"] == 2

    # 5. Finish run
    finish = client.post(f"/api/runs/{run_id}/finish")
    assert finish.status_code == 200
    finish_data = finish.json()
    assert finish_data["status"] == "completed"
    assert finish_data["total_tests"] == 2
    assert finish_data["passed"] == 1
    assert finish_data["failed"] == 1
    assert finish_data["success_rate"] == 50.0
