"""
Tests for /api/v1/predict endpoint
"""

from fastapi import status
from fastapi.testclient import TestClient


def test_prediction_valid(client: TestClient, valid_patient_dict: dict):
    """Verifies that a complete valid patient record yields valid predictions for all 4 targets."""
    payload = {"patient": valid_patient_dict}
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "predictions" in data
    preds = data["predictions"]
    assert set(preds.keys()) == {"cath", "lad", "lcx", "rca"}

    # Probability bounds & threshold verification
    for target, pred in preds.items():
        assert 0.0 <= pred["probability"] <= 1.0
        assert 0.0 <= pred["threshold"] <= 1.0

        if target == "cath":
            expected_class = "CAD" if pred["probability"] >= pred["threshold"] else "Normal"
        else:
            expected_class = "Stenotic" if pred["probability"] >= pred["threshold"] else "Normal"

        assert pred["prediction"] == expected_class


def test_prediction_determinism(client: TestClient, valid_patient_dict: dict):
    """Verifies that identical patient inputs produce identical prediction outputs."""
    payload = {"patient": valid_patient_dict}
    res1 = client.post("/api/v1/predict", json=payload).json()
    res2 = client.post("/api/v1/predict", json=payload).json()

    for target in ["cath", "lad", "lcx", "rca"]:
        assert res1["predictions"][target]["probability"] == res2["predictions"][target]["probability"]
        assert res1["predictions"][target]["prediction"] == res2["predictions"][target]["prediction"]


def test_prediction_target_leakage_rejection(client: TestClient, valid_patient_dict: dict):
    """Verifies strict 422 rejection when ground-truth target is included in input."""
    leaked_payload = dict(valid_patient_dict)
    leaked_payload["Cath"] = "CAD"

    response = client.post("/api/v1/predict", json={"patient": leaked_payload})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"
    assert "TARGET LEAKAGE DETECTED" in data["error"]["message"]


def test_prediction_missing_feature_rejection(client: TestClient, valid_patient_dict: dict):
    """Verifies 422 rejection when required feature is omitted."""
    incomplete = dict(valid_patient_dict)
    del incomplete["Age"]

    response = client.post("/api/v1/predict", json={"patient": incomplete})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"
    assert "Missing required clinical feature" in data["error"]["message"]


def test_prediction_categorical_normalization(client: TestClient, valid_patient_dict: dict):
    """Verifies that non-standard casing and documented typos ('Fmale', 'mild') are normalized."""
    tolerant_patient = dict(valid_patient_dict)
    tolerant_patient["Sex"] = "Fmale"
    tolerant_patient["VHD"] = "mild"

    response = client.post("/api/v1/predict", json={"patient": tolerant_patient})
    assert response.status_code == status.HTTP_200_OK
    assert "predictions" in response.json()


def test_prediction_invalid_categorical_rejection(client: TestClient, valid_patient_dict: dict):
    """Verifies 422 rejection when an invalid categorical string is supplied."""
    invalid_patient = dict(valid_patient_dict)
    invalid_patient["Sex"] = "UnknownGender"

    response = client.post("/api/v1/predict", json={"patient": invalid_patient})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"
