"""
Tests for /api/v1/health endpoint
"""

from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient


def test_health_success(client: TestClient):
    """Verifies standard operational health status."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "corovista-api"
    assert "version" in data
    assert data["models_loaded"] is True


def test_health_degraded_on_failure(client: TestClient):
    """Verifies that health endpoint reports 503 degraded status if models fail."""
    with patch("backend.app.api.routes.health.load_all_models", side_effect=RuntimeError("Disk failure")):
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "degraded"
        assert data["models_loaded"] is False
