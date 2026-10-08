"""
Tests for /api/v1/models and /api/v1/features endpoints
"""

from fastapi import status
from fastapi.testclient import TestClient


def test_models_metadata(client: TestClient):
    """Verifies model inventory metadata for all four prediction targets."""
    response = client.get("/api/v1/models")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "models" in data
    models = {m["target"]: m for m in data["models"]}

    assert set(models.keys()) == {"cath", "lad", "lcx", "rca"}

    # Verify thresholds
    assert models["cath"]["threshold"] == 0.50
    assert models["lad"]["threshold"] == 0.50
    assert models["lcx"]["threshold"] == 0.50
    assert models["rca"]["threshold"] == 0.38

    # Verify model types & calibration
    assert models["cath"]["model"] == "XGBoost"
    assert models["cath"]["calibrated"] is True
    assert models["cath"]["positive_label"] == "CAD"
    assert models["cath"]["negative_label"] == "Normal"

    assert models["lad"]["model"] == "XGBoost"
    assert models["lad"]["calibrated"] is True
    assert models["lad"]["positive_label"] == "Stenotic"

    assert models["lcx"]["model"] == "XGBoost"
    assert models["lcx"]["calibrated"] is False
    assert models["lcx"]["positive_label"] == "Stenotic"

    assert models["rca"]["model"] == "LogisticRegression"
    assert models["rca"]["calibrated"] is True
    assert models["rca"]["positive_label"] == "Stenotic"

    # Verify explanation space is explicitly documented
    for m in models.values():
        assert m["explanation_space"] == "log-odds (model score)"

    # Verify no file paths leaked
    raw_text = response.text
    assert ".joblib" not in raw_text
    assert "models/" not in raw_text


def test_features_metadata(client: TestClient):
    """Verifies feature registry completeness, categorization, and absence of target leakage."""
    response = client.get("/api/v1/features")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "features" in data
    assert data["total_features"] == 54
    features = data["features"]

    feature_names = [f["machine_name"] for f in features]

    # Target leakage check: targets must never be in feature registry
    for forbidden in ["Cath", "LAD", "LCX", "RCA", "cath", "lad", "lcx", "rca"]:
        assert forbidden not in feature_names

    # Check categories
    valid_categories = {
        "Demographic",
        "Symptoms / Examination",
        "ECG",
        "Laboratory / Echo",
    }
    for f in features:
        assert f["category"] in valid_categories
        assert f["type"] in {"numeric", "binary", "categorical"}
        assert f["human_readable_label"] is not None
        assert len(f["human_readable_label"]) > 0

    # Specific feature checks
    sex_feat = next(f for f in features if f["machine_name"] == "Sex")
    assert sex_feat["type"] == "categorical"
    assert set(sex_feat["allowed_values"]) == {"Male", "Female"}

    vhd_feat = next(f for f in features if f["machine_name"] == "VHD")
    assert vhd_feat["type"] == "categorical"
    assert "Mild" in vhd_feat["allowed_values"]

    age_feat = next(f for f in features if f["machine_name"] == "Age")
    assert age_feat["type"] == "numeric"
    assert age_feat["simulator_validation_range"] is not None
    assert age_feat["simulator_validation_range"]["min"] == 18.0
    assert age_feat["simulator_validation_range"]["max"] == 100.0
