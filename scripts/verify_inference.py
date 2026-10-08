"""
CoroVista - Stage 3 Inference & Explainability Verification Script
Multimodal AI Hackathon 2026 — Track A

Performs comprehensive verification:
1. Loads all four final serialized models (Cath, LAD, LCX, RCA).
2. Verifies prediction output schema, probability bounds [0, 1], and target thresholds.
3. Tests categorical normalizations ('Fmale' -> 'Female', VHD casing).
4. Verifies determinism (repeated identical inference).
5. Tests strict target leakage prevention (rejects 'Cath', 'LAD', 'LCX', 'RCA').
6. Validates patient-level SHAP explanation generation.
7. Computes and exports global SHAP explanations to data/reports/shap_global.json and plots.
"""

from pathlib import Path
import sys

# Ensure project root and src are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import logging
import pandas as pd
import numpy as np

from ml.preprocessing.pipeline import load_dataset, extract_features_and_targets
from src.corovista.inference.loader import load_all_models
from src.corovista.inference.predictor import predict_patient
from src.corovista.explainability.patient_explanations import (
    explain_patient,
    top_positive_contributors,
    top_negative_contributors,
)
from src.corovista.explainability.global_explanations import compute_global_explanations

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_inference")

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
SHAP_PLOTS_DIR = REPORTS_DIR / "shap"


def main():
    logger.info("=== STEP 1: Verifying Model Pipeline Artifacts ===")
    models = load_all_models(models_root=PROJECT_ROOT / "models")
    expected_targets = {"cath", "lad", "lcx", "rca"}
    assert set(models.keys()) == expected_targets, f"Expected targets {expected_targets}, got {set(models.keys())}"
    logger.info("Successfully loaded all 4 model pipelines:")
    for t_key, info in models.items():
        logger.info(
            "  - %s: Model=%s, Calibration=%s, Threshold=%.2f",
            t_key.upper(), info["model_family"], info["calibration"], info["threshold"]
        )

    # Threshold checks
    assert models["cath"]["threshold"] == 0.50
    assert models["lad"]["threshold"] == 0.50
    assert models["lcx"]["threshold"] == 0.50
    assert models["rca"]["threshold"] == 0.38

    logger.info("\n=== STEP 2: Loading Raw Dataset & Selecting Representative Patients ===")
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets_raw = extract_features_and_targets(df_raw)

    # Representative patients:
    # Patient 0: Typical presentation
    # Patient 93: Target anomaly (LAD=Stenotic, LCX=Normal, RCA=Normal, Cath=Normal)
    # Patient 10: Low-risk female
    test_indices = [0, 93, 10]

    logger.info("\n=== STEP 3: Running Inference & Schema Verification ===")
    for idx in test_indices:
        patient_record = X_raw.iloc[idx].to_dict()
        res = predict_patient(patient_record)

        logger.info("Patient Index %d Results:", idx)
        for t_name in ["cath", "lad", "lcx", "rca"]:
            pred = getattr(res, t_name)
            logger.info(
                "  - %s: prob=%.4f, pred=%s (threshold=%.2f, model=%s)",
                t_name.upper(), pred.probability, pred.prediction, pred.threshold, pred.model_family
            )
            # Verify probability bounds
            assert 0.0 <= pred.probability <= 1.0, f"Probability {pred.probability} out of bounds!"
            # Verify threshold logic
            expected_class = 1 if pred.probability >= pred.threshold else 0
            if t_name == "cath":
                expected_label = "CAD" if expected_class == 1 else "Normal"
            else:
                expected_label = "Stenotic" if expected_class == 1 else "Normal"
            assert pred.prediction == expected_label, (
                f"Mismatch for {t_name}: prob={pred.probability}, thresh={pred.threshold}, got {pred.prediction}, expected {expected_label}"
            )

    logger.info("\n=== STEP 4: Verifying Categorical Normalization ===")
    # Test 'Fmale' typo and mixed VHD casing
    sample_pt = X_raw.iloc[0].to_dict()
    sample_pt["Sex"] = "Fmale"
    sample_pt["VHD"] = "mild"
    sample_pt["BBB"] = "N"
    res_norm = predict_patient(sample_pt)
    assert res_norm.cath.probability is not None
    logger.info("Successfully normalized 'Fmale' and 'mild' without errors.")

    logger.info("\n=== STEP 5: Verifying Determinism (Repeated Identical Inference) ===")
    res_run1 = predict_patient(sample_pt, return_dict=True)
    res_run2 = predict_patient(sample_pt, return_dict=True)
    assert res_run1 == res_run2, "Inference is not deterministic across runs!"
    logger.info("Determinism confirmed: run 1 and run 2 produced identical probability outputs.")

    logger.info("\n=== STEP 6: Verifying Target Leakage Prevention ===")
    leak_pt = dict(sample_pt)
    for bad_col in ["Cath", "LAD", "LCX", "RCA"]:
        leak_pt_copy = dict(leak_pt)
        leak_pt_copy[bad_col] = "Normal"
        try:
            predict_patient(leak_pt_copy)
            raise AssertionError(f"Security failure: Input with leaked column '{bad_col}' was accepted!")
        except ValueError as e:
            assert "TARGET LEAKAGE DETECTED" in str(e)
    logger.info("Target leakage prevention verified: All ground-truth targets strictly rejected.")

    logger.info("\n=== STEP 7: Verifying Patient-Level SHAP Explanations ===")
    exp_cath = explain_patient(sample_pt, target="cath", max_features=10)
    assert exp_cath["target"] == "cath"
    assert "log-odds" in exp_cath["explanation_space"]
    assert len(exp_cath["features"]) == 10
    top_pos = top_positive_contributors(exp_cath, n=3)
    top_neg = top_negative_contributors(exp_cath, n=3)
    logger.info("Patient 0 Cath SHAP base value: %.4f", exp_cath["base_value"])
    logger.info("Top Positive Drivers (Risk Elevating):")
    for f in top_pos:
        logger.info("  + %s (%s): SHAP=+%.4f", f["label"], f["feature"], f["shap_value"])
    logger.info("Top Negative Drivers (Protective):")
    for f in top_neg:
        logger.info("  - %s (%s): SHAP=%.4f", f["label"], f["feature"], f["shap_value"])

    # Test patient explanations for all other targets
    for t in ["lad", "lcx", "rca"]:
        exp = explain_patient(sample_pt, target=t, max_features=5)
        assert exp["target"] == t
        assert len(exp["features"]) == 5
        logger.info("Successfully generated explanation for target %s (base value: %.4f)", t.upper(), exp["base_value"])

    logger.info("\n=== STEP 8: Computing Global Cohort SHAP & Generating Plots ===")
    json_path = REPORTS_DIR / "shap_global.json"
    global_results = compute_global_explanations(
        df_raw, output_json_path=json_path, plots_dir=SHAP_PLOTS_DIR
    )
    assert json_path.exists(), f"Global SHAP JSON report not found at {json_path}"
    logger.info("Exported global SHAP report to %s", json_path)
    for t in ["cath", "lad", "lcx", "rca"]:
        plot_p = SHAP_PLOTS_DIR / f"{t}_summary.png"
        assert plot_p.exists(), f"Expected plot not found: {plot_p}"
        logger.info("  - Verified summary plot for %s: %s", t.upper(), plot_p)

    logger.info("\n========================================================")
    logger.info("STAGE 3 INFERENCE & EXPLAINABILITY VERIFICATION COMPLETE!")
    logger.info("All assertions passed. Production contracts verified.")
    logger.info("========================================================")


if __name__ == "__main__":
    main()
