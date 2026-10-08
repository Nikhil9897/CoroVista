"""
Tests for /api/v1/analyze combined endpoint
"""

from fastapi import status
from fastapi.testclient import TestClient


def test_analyze_valid(client: TestClient, valid_patient_dict: dict):
    """Verifies complete multi-target prediction and SHAP explanation payload."""
    payload = {"patient": valid_patient_dict}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "predictions" in data
    assert set(data["predictions"].keys()) == {"cath", "lad", "lcx", "rca"}

    assert "explanations" in data
    assert set(data["explanations"].keys()) == {"cath", "lad", "lcx", "rca"}

    # Disclaimers check
    assert "clinical_disclaimer" in data
    assert "Educational and decision-support prototype only" in data["clinical_disclaimer"]

    assert "visualization_note" in data
    assert "not physical 3D lesion coordinates" in data["visualization_note"]


def test_analyze_target_leakage_rejection(client: TestClient, valid_patient_dict: dict):
    """Verifies 422 rejection when target leakage is present."""
    leaked = dict(valid_patient_dict)
    leaked["LCX"] = "Normal"

    response = client.post("/api/v1/analyze", json={"patient": leaked})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"


def test_analyze_malformed_request(client: TestClient):
    """Verifies 422 rejection when patient object is missing."""
    response = client.post("/api/v1/analyze", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"
