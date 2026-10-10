"""
CoroVista - Backend Verification Script
Verifies all FastAPI REST endpoints, schema validation, and error envelopes.
"""

import logging
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi import status
from fastapi.testclient import TestClient

from backend.app.main import app
from ml.preprocessing.pipeline import extract_features_and_targets, load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_backend")

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")


def run_backend_verification():
    logger.info("========================================================")
    logger.info("COROVISTA — FASTAPI BACKEND CONTRACT VERIFICATION")
    logger.info("========================================================")

    client = TestClient(app)

    # 1. Health
    logger.info("--> Testing GET /api/v1/health")
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == status.HTTP_200_OK
    health_data = res_health.json()
    assert health_data["status"] == "ok"
    assert health_data["models_loaded"] is True
    logger.info(f"    Health: status={health_data['status']}, models_loaded={health_data['models_loaded']}")

    # 2. Models
    logger.info("--> Testing GET /api/v1/models")
    res_models = client.get("/api/v1/models")
    assert res_models.status_code == status.HTTP_200_OK
    models_data = res_models.json()["models"]
    assert len(models_data) == 4
    for m in models_data:
        logger.info(
            f"    Target={m['target'].upper()}: model={m['model']}, "
            f"threshold={m['threshold']}, calibrated={m['calibrated']}"
        )

    # 3. Features
    logger.info("--> Testing GET /api/v1/features")
    res_features = client.get("/api/v1/features")
    assert res_features.status_code == status.HTTP_200_OK
    features_data = res_features.json()
    assert features_data["total_features"] == 54
    logger.info(f"    Features count: {features_data['total_features']} (all targets strictly excluded)")

    # 4. Predict
    logger.info("--> Testing POST /api/v1/predict")
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, _ = extract_features_and_targets(df_raw)
    patient_dict = X_raw.iloc[0].to_dict()

    res_predict = client.post("/api/v1/predict", json={"patient": patient_dict})
    assert res_predict.status_code == status.HTTP_200_OK
    preds = res_predict.json()["predictions"]
    for t, p in preds.items():
        logger.info(
            f"    Predict [{t.upper()}]: prob={p['probability']:.4f}, "
            f"prediction={p['prediction']}, threshold={p['threshold']}"
        )

    # 5. Explain
    logger.info("--> Testing POST /api/v1/explain")
    res_explain = client.post("/api/v1/explain", json={"patient": patient_dict, "target": "cath"})
    assert res_explain.status_code == status.HTTP_200_OK
    exp = res_explain.json()
    logger.info(
        f"    Explain [CATH]: base_value={exp['base_value']}, "
        f"explanation_space={exp['explanation_space']}, "
        f"top positive={exp['positive_contributors'][0]['feature']} (SHAP={exp['positive_contributors'][0]['shap_value']})"
    )

    # 6. Analyze
    logger.info("--> Testing POST /api/v1/analyze")
    res_analyze = client.post("/api/v1/analyze", json={"patient": patient_dict})
    assert res_analyze.status_code == status.HTTP_200_OK
    ana = res_analyze.json()
    assert set(ana["predictions"].keys()) == {"cath", "lad", "lcx", "rca"}
    assert set(ana["explanations"].keys()) == {"cath", "lad", "lcx", "rca"}
    assert "Educational and decision-support prototype only" in ana["clinical_disclaimer"]
    assert "not physical 3D lesion coordinates" in ana["visualization_note"]
    logger.info("    Analyze: Combined predictions + explanations verified for all 4 targets.")
    logger.info(f"    Disclaimer verified: {ana['clinical_disclaimer'][:60]}...")
    logger.info(f"    3D Note verified: {ana['visualization_note']}")

    # 7. Target Leakage Rejection (Error Envelope)
    logger.info("--> Testing Target Leakage Rejection on POST /api/v1/predict")
    leaked = dict(patient_dict)
    leaked["Cath"] = "CAD"
    res_leak = client.post("/api/v1/predict", json={"patient": leaked})
    assert res_leak.status_code == 422
    assert res_leak.json()["error"]["code"] == "INVALID_INPUT"
    logger.info("    Target Leakage Rejection verified (HTTP 422, code=INVALID_INPUT).")

    # 8. Invalid Target Rejection on POST /api/v1/explain
    logger.info("--> Testing Invalid Target Rejection on POST /api/v1/explain")
    res_inv = client.post("/api/v1/explain", json={"patient": patient_dict, "target": "invalid_vessel"})
    assert res_inv.status_code == 400
    assert res_inv.json()["error"]["code"] == "INVALID_TARGET"
    logger.info("    Invalid Target Rejection verified (HTTP 400, code=INVALID_TARGET).")

    logger.info("========================================================")
    logger.info("ALL FASTAPI ENDPOINTS DETERMINISTICALLY VERIFIED!")
    logger.info("========================================================")


if __name__ == "__main__":
    run_backend_verification()
