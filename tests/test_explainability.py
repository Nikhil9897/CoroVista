"""
CoroVista - Stage 3 SHAP Explainability Unit & Integration Tests

Tests:
1. Explainer initialization across all 4 targets (Cath, LAD, LCX, RCA)
2. Additivity property of SHAP values
3. Patient-level explanation contract and schema
4. Ranking by absolute SHAP value descending
5. Positive and negative contributor helper functions
6. Transformed feature name to human-readable label mapping
7. Calibration space metadata disclosure
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.corovista.explainability.explainers import get_target_explainer
from src.corovista.explainability.feature_mapping import get_human_label, get_feature_description
from src.corovista.explainability.patient_explanations import (
    explain_patient,
    top_positive_contributors,
    top_negative_contributors,
)
from ml.preprocessing.pipeline import load_dataset, extract_features_and_targets

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")


@pytest.fixture(scope="session")
def sample_patient_dict():
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, _ = extract_features_and_targets(df_raw)
    return X_raw.iloc[0].to_dict()


# 1. Explainer Initialization
def test_get_target_explainer():
    for target in ["cath", "lad", "lcx", "rca"]:
        exp = get_target_explainer(target)
        assert exp.target == target
        assert len(exp.feature_names) == 57
        assert "log-odds" in exp.explanation_space


# 2. Additivity Property
def test_shap_additivity_property(sample_patient_dict):
    # LCX is single XGBoost model - exact margin additivity test
    exp_lcx = get_target_explainer("lcx")
    from src.corovista.inference.validation import validate_and_normalize_patient_input
    clean_df = validate_and_normalize_patient_input(sample_patient_dict)

    shap_vals, base_val = exp_lcx.explain(clean_df)
    X_trans = exp_lcx.transform_features(clean_df)

    # Compute raw margin directly from booster
    import xgboost as xgb
    dmat = xgb.DMatrix(X_trans, feature_names=exp_lcx.feature_names)
    raw_margin = float(exp_lcx.classifier.get_booster().predict(dmat, output_margin=True)[0])

    sum_shap = float(np.sum(shap_vals[0]) + base_val)
    assert np.isclose(sum_shap, raw_margin, atol=1e-5), f"SHAP sum {sum_shap} != raw margin {raw_margin}"


# 3. Patient Explanation Structure
def test_explain_patient_contract(sample_patient_dict):
    res = explain_patient(sample_patient_dict, target="cath")
    assert res["target"] == "cath"
    assert "log-odds" in res["explanation_space"]
    assert "calibration_note" in res
    assert isinstance(res["base_value"], float)
    assert isinstance(res["features"], list)
    assert len(res["features"]) == 57

    item = res["features"][0]
    assert "feature" in item
    assert "label" in item
    assert "value" in item
    assert "shap_value" in item
    assert "direction" in item
    assert item["direction"] in ["positive", "negative"]


# 4. Sorting by Absolute SHAP Descending
def test_explain_patient_sorting(sample_patient_dict):
    res = explain_patient(sample_patient_dict, target="lad")
    abs_shaps = [abs(f["shap_value"]) for f in res["features"]]
    for i in range(len(abs_shaps) - 1):
        assert abs_shaps[i] >= abs_shaps[i + 1]


# 5. Top Positive & Negative Contributors
def test_top_contributors(sample_patient_dict):
    res = explain_patient(sample_patient_dict, target="cath")
    pos = top_positive_contributors(res, n=3)
    neg = top_negative_contributors(res, n=3)

    assert len(pos) <= 3
    assert len(neg) <= 3

    for p in pos:
        assert p["shap_value"] > 0
    for n in neg:
        assert n["shap_value"] < 0


# 6. Feature Mapping Completeness
def test_feature_mapping():
    assert get_human_label("Age") == "Patient Age (years)"
    assert get_human_label("Typical Chest Pain") == "Typical Anginal Chest Pain"
    assert get_human_label("EF-TTE") == "Left Ventricular Ejection Fraction (% Echo)"
    assert get_human_label("BBB_RBBB") == "Right Bundle Branch Block (ECG)"
    assert get_human_label("VHD_Moderate") == "Moderate Valvular Heart Disease (Echo)"

    desc = get_feature_description("EF-TTE")
    assert "echocardiography" in desc.lower()


# 7. Calibration Space Disclosure
def test_calibration_disclosure(sample_patient_dict):
    for t in ["cath", "lad", "rca"]:
        res = explain_patient(sample_patient_dict, target=t)
        assert "probability calibration is applied separately" in res["calibration_note"]
