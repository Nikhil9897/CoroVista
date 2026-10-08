"""
Tests for /api/v1/explain endpoint
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.parametrize("target", ["cath", "lad", "lcx", "rca"])
def test_explanation_all_targets(client: TestClient, valid_patient_dict: dict, target: str):
    """Verifies patient-level SHAP explanation generation across all four targets."""
    payload = {
        "patient": valid_patient_dict,
        "target": target,
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["target"] == target
    assert data["explanation_space"] == "log-odds (model score)"
    assert "calibration_disclosure" in data
    assert "probability calibration is applied separately" in data["calibration_disclosure"]
    assert "base_value" in data
    assert isinstance(data["base_value"], float)

    # Features list structure
    features = data["features"]
    assert len(features) > 0
    first = features[0]
    assert "feature" in first
    assert "label" in first
    assert "value" in first
    assert "shap_value" in first
    assert first["direction"] in ["positive", "negative"]

    # Verify positive and negative contributors lists
    assert "positive_contributors" in data
    assert "negative_contributors" in data
    for item in data["positive_contributors"]:
        assert item["shap_value"] > 0
        assert item["direction"] == "positive"
    for item in data["negative_contributors"]:
        assert item["shap_value"] < 0
        assert item["direction"] == "negative"


def test_explanation_invalid_target_rejection(client: TestClient, valid_patient_dict: dict):
    """Verifies 400 rejection when requesting explanation for an invalid target."""
    payload = {
        "patient": valid_patient_dict,
        "target": "non_existent_target",
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "INVALID_TARGET"


def test_explanation_target_leakage_rejection(client: TestClient, valid_patient_dict: dict):
    """Verifies 422 rejection when target column is present in input."""
    leaked = dict(valid_patient_dict)
    leaked["RCA"] = "Stenotic"

    response = client.post("/api/v1/explain", json={"patient": leaked, "target": "cath"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"
