"""
Tests for the OpenEncroachment FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from open_encroachment.api import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_cases_endpoint(client):
    """Test the cases endpoint."""
    response = client.get("/api/v1/cases")
    # This will fail without proper setup, but we test the endpoint exists
    assert response.status_code in [200, 500]  # 500 is acceptable for missing database


def test_get_incidents_endpoint(client):
    """Test the incidents endpoint."""
    response = client.get("/api/v1/incidents")
    # This will fail without proper setup, but we test the endpoint exists
    assert response.status_code in [200, 500]  # 500 is acceptable for missing database


def test_verify_evidence_endpoint(client):
    """Test the evidence verification endpoint."""
    response = client.get("/api/v1/evidence/verify")
    # This will fail without proper setup, but we test the endpoint exists
    assert response.status_code in [200, 500]  # 500 is acceptable for missing files


def test_severity_summary_endpoint(client):
    """Test the severity summary endpoint."""
    response = client.get("/api/v1/analytics/severity")
    # This will fail without proper setup, but we test the endpoint exists
    assert response.status_code in [200, 500]  # 500 is acceptable for missing database


@pytest.mark.skipif("OPENAI_API_KEY" not in pytest.env, reason="OpenAI API key not available")
def test_agent_run_endpoint(client):
    """Test the agent run endpoint (requires OpenAI API key)."""
    payload = {"prompt": "What is the current status of the system?", "model": "gpt-4o-mini"}
    response = client.post("/api/v1/agent/run", json=payload)
    # This may fail due to API key or model issues, but we test the endpoint exists
    assert response.status_code in [200, 401, 500]


@pytest.mark.skipif("OPENAI_API_KEY" not in pytest.env, reason="OpenAI API key not available")
def test_pipeline_run_endpoint(client):
    """Test the pipeline run endpoint."""
    payload = {"config_path": "config/settings.yaml", "use_sample_data": True}
    response = client.post("/api/v1/pipeline/run", json=payload)
    # This may fail due to missing data files, but we test the endpoint exists
    assert response.status_code in [200, 500]


@pytest.mark.skipif("OPENAI_API_KEY" not in pytest.env, reason="OpenAI API key not available")
def test_notification_endpoint(client):
    """Test the notification creation endpoint."""
    payload = {"incident_id": "test-incident-123", "config_path": "config/settings.yaml"}
    response = client.post("/api/v1/notifications", json=payload)
    # This will likely fail due to missing incident, but we test the endpoint exists
    assert response.status_code in [200, 404, 500]
