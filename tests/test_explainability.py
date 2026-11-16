"""
CoroVista - SHAP Explainability Unit & Integration Tests

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

import numpy as np
import pytest
import xgboost as xgb
from scipy.special import expit, logit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.preprocessing.pipeline import (
    build_preprocessing_pipeline,
    extract_features_and_targets,
    load_dataset,
)
from ml.training.trainer import create_final_pipeline
from src.corovista.explainability.explainers import TargetExplainer, get_target_explainer
from src.corovista.explainability.feature_mapping import get_feature_description, get_human_label
from src.corovista.explainability.patient_explanations import (
    explain_patient,
    top_negative_contributors,
    top_positive_contributors,
)
from src.corovista.inference.validation import validate_and_normalize_patient_input

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
    """Verifies that patient-level explanations explicitly disclose the log-odds space and calibration boundary."""
    for t in ["cath", "lad", "lcx", "rca"]:
        res = explain_patient(sample_patient_dict, target=t)
        assert res["explanation_space"] == "log-odds (model score)"
        assert "probability calibration is applied separately" in res["calibration_note"]
        assert "probability calibration is applied separately" in res["calibration_disclosure"]
        assert "log-odds" in res["calibration_disclosure"]


# 8. Pipeline Architecture Regression Tests (Legacy vs New Calibrated Structures)
def test_explain_legacy_uncalibrated_pipeline(sample_patient_dict):
    """Verifies TargetExplainer works with legacy uncalibrated Pipeline structure."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)
    y = targets["LCX"]

    prep = build_preprocessing_pipeline(vhd_encoding="onehot", scaler_type="none")
    legacy_xgb = XGBClassifier(n_estimators=10, max_depth=3, random_state=42)
    legacy_pipe = Pipeline([("preprocessing", prep), ("classifier", legacy_xgb)])
    legacy_pipe.fit(X_raw, y)

    meta = {"model_family": "XGBoost", "calibration_method": "uncalibrated"}
    explainer = TargetExplainer("lcx_legacy", pipeline=legacy_pipe, metadata=meta)

    clean_df = validate_and_normalize_patient_input(sample_patient_dict)
    shap_vals, base_val = explainer.explain(clean_df)

    assert shap_vals.shape == (1, 57)
    assert isinstance(base_val, float)
    assert len(explainer.feature_names) == 57

    # Additivity on raw margin
    X_trans = explainer.transform_features(clean_df)
    dmat = xgb.DMatrix(X_trans, feature_names=explainer.feature_names)
    raw_margin = float(legacy_xgb.get_booster().predict(dmat, output_margin=True)[0])
    sum_shap = float(np.sum(shap_vals[0]) + base_val)
    assert np.isclose(sum_shap, raw_margin, atol=1e-5)


def test_explain_new_calibrated_logistic_regression(sample_patient_dict):
    """Verifies TargetExplainer works with new CalibratedClassifierCV-wrapped Logistic Regression."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)
    y = targets["RCA"]

    cal_pipe = create_final_pipeline(
        "LogisticRegression",
        scaler_type="standard",
        calibration_method="sigmoid",
        random_state=42,
        y=y,
    )
    assert isinstance(cal_pipe, CalibratedClassifierCV)
    cal_pipe.fit(X_raw, y)

    meta = {"model_family": "LogisticRegression", "calibration_method": "sigmoid"}
    explainer = TargetExplainer("rca_new", pipeline=cal_pipe, metadata=meta)

    clean_df = validate_and_normalize_patient_input(sample_patient_dict)
    shap_vals, base_val = explainer.explain(clean_df)

    assert shap_vals.shape == (1, 57)
    assert isinstance(base_val, float)
    assert len(explainer.feature_names) == 57
    assert not np.isnan(shap_vals).any()

    # Verify additivity: sum(shap) + base_val equals average decision function across folds
    fold_margins = []
    for cal_clf in cal_pipe.calibrated_classifiers_:
        fold_prep = cal_clf.estimator.named_steps["preprocessing"]
        fold_clf = cal_clf.estimator.named_steps["classifier"]
        x_fold = fold_prep.transform(clean_df)
        fold_margins.append(float(fold_clf.decision_function(x_fold)[0]))
    expected_margin = float(np.mean(fold_margins))
    sum_shap = float(np.sum(shap_vals[0]) + base_val)
    assert np.isclose(sum_shap, expected_margin, atol=1e-5)


def test_explain_new_calibrated_xgboost(sample_patient_dict):
    """Verifies TargetExplainer works with new CalibratedClassifierCV-wrapped XGBoost."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)
    y = targets["Cath"]

    cal_pipe = create_final_pipeline(
        "XGBoost",
        scaler_type="none",
        calibration_method="sigmoid",
        random_state=42,
        y=y,
    )
    assert isinstance(cal_pipe, CalibratedClassifierCV)
    cal_pipe.fit(X_raw, y)

    meta = {"model_family": "XGBoost", "calibration_method": "sigmoid"}
    explainer = TargetExplainer("cath_new", pipeline=cal_pipe, metadata=meta)

    clean_df = validate_and_normalize_patient_input(sample_patient_dict)
    shap_vals, base_val = explainer.explain(clean_df)

    assert shap_vals.shape == (1, 57)
    assert isinstance(base_val, float)
    assert len(explainer.feature_names) == 57
    assert not np.isnan(shap_vals).any()

    # Exact additivity check against average booster margin across folds
    fold_margins = []
    for cal_clf in cal_pipe.calibrated_classifiers_:
        fold_prep = cal_clf.estimator.named_steps["preprocessing"]
        fold_clf = cal_clf.estimator.named_steps["classifier"]
        x_fold = fold_prep.transform(clean_df)
        dmat = xgb.DMatrix(x_fold, feature_names=explainer.feature_names)
        margin = float(fold_clf.get_booster().predict(dmat, output_margin=True)[0])
        fold_margins.append(margin)
    expected_margin = float(np.mean(fold_margins))
    sum_shap = float(np.sum(shap_vals[0]) + base_val)
    assert np.isclose(sum_shap, expected_margin, atol=1e-5)


@pytest.mark.parametrize("n_splits", [2, 4])
def test_explain_multiple_calibration_folds(sample_patient_dict, n_splits):
    """Verifies TargetExplainer handles arbitrary numbers of calibration folds."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)
    y = targets["LAD"]

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    cal_pipe = create_final_pipeline(
        "XGBoost",
        scaler_type="none",
        calibration_method="sigmoid",
        cv=skf,
        y=y,
    )
    cal_pipe.fit(X_raw, y)
    assert len(cal_pipe.calibrated_classifiers_) == n_splits

    meta = {"model_family": "XGBoost", "calibration_method": "sigmoid"}
    explainer = TargetExplainer(f"lad_{n_splits}folds", pipeline=cal_pipe, metadata=meta)

    clean_df = validate_and_normalize_patient_input(sample_patient_dict)
    shap_vals, base_val = explainer.explain(clean_df)

    assert shap_vals.shape == (1, 57)
    assert not np.isnan(shap_vals).any()
    assert isinstance(base_val, float)


def test_explain_batch_input_shape_and_feature_alignment():
    """Verifies explanation output shape and feature alignment across multi-patient batches."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)
    y = targets["Cath"]

    cal_pipe = create_final_pipeline(
        "XGBoost",
        scaler_type="none",
        calibration_method="sigmoid",
        random_state=42,
        y=y,
    )
    cal_pipe.fit(X_raw, y)
    meta = {"model_family": "XGBoost", "calibration_method": "sigmoid"}
    explainer = TargetExplainer("cath_batch", pipeline=cal_pipe, metadata=meta)

    batch_df = X_raw.iloc[:10]
    shap_vals, base_val = explainer.explain(batch_df)

    assert shap_vals.shape == (10, 57)
    assert isinstance(base_val, float)
    assert len(explainer.feature_names) == 57

    # Ensure feature alignment with feature labels
    for f in explainer.feature_names:
        label = get_human_label(f)
        assert label is not None
        assert len(label) > 0


def test_explain_error_handling():
    """Verifies that unsupported or corrupted configurations raise informative errors."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)

    # 1. Unfitted pipeline raises clear ValueError
    unfitted_pipe = Pipeline([
        ("preprocessing", build_preprocessing_pipeline()),
        ("classifier", LogisticRegression()),
    ])
    with pytest.raises(ValueError, match="Preprocessing pipeline must be fitted before initializing TargetExplainer"):
        TargetExplainer("unfitted", pipeline=unfitted_pipe, metadata={"model_family": "LogisticRegression"})

    # 2. Unsupported model family raises NotImplementedError
    fitted_pipe = Pipeline([
        ("preprocessing", build_preprocessing_pipeline(scaler_type="standard")),
        ("classifier", LogisticRegression(max_iter=500)),
    ])
    fitted_pipe.fit(X_raw, targets["Cath"])
    explainer = TargetExplainer("unsupported", pipeline=fitted_pipe, metadata={"model_family": "UnsupportedModel"})
    with pytest.raises(NotImplementedError, match="Unsupported model family for explanation"):
        explainer.explain(X_raw.iloc[:2])


# 9. Scientific Numerical Validation: Explanation Reconstruction vs Calibrated Output
@pytest.mark.parametrize("model_family,target_key,scaler", [
    ("LogisticRegression", "RCA", "standard"),
    ("XGBoost", "Cath", "none"),
])
def test_scientific_numerical_validation_reconstruction_vs_calibrated_output(
    model_family, target_key, scaler
):
    """
    Scientific validation comparing SHAP explanation reconstruction with actual pipeline outputs.

    Verifies:
    1. Exact Additivity: Sum of SHAP values + base value reconstructs the average uncalibrated
       fold margin/log-odds exactly (within 1e-5).
    2. Mathematical Non-Equivalence with Calibrated Output: Demonstrates that the uncalibrated
       score reconstruction differs from both calibrated probability and logit(calibrated probability),
       proving why SHAP values must be strictly labeled as log-odds model scores, not calibrated probabilities.
    3. Proper Metadata Space Attribution: Verifies explanation_space reflects 'log-odds (model score)'.
    """
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, targets = extract_features_and_targets(df_raw)
    y = targets[target_key]

    cal_pipe = create_final_pipeline(
        model_family,
        scaler_type=scaler,
        calibration_method="sigmoid",
        random_state=42,
        y=y,
    )
    cal_pipe.fit(X_raw, y)

    meta = {"model_family": model_family, "calibration_method": "sigmoid"}
    explainer = TargetExplainer(target_key.lower(), pipeline=cal_pipe, metadata=meta)

    sample_x = X_raw.iloc[:10]
    shap_vals, base_val = explainer.explain(sample_x)

    # 1. Reconstruct model score from SHAP
    reconstructed_margin = np.sum(shap_vals, axis=1) + base_val

    # Compute expected mean uncalibrated margin across folds
    fold_margins = []
    for cal_clf in cal_pipe.calibrated_classifiers_:
        fold_prep = cal_clf.estimator.named_steps["preprocessing"]
        fold_clf = cal_clf.estimator.named_steps["classifier"]
        x_trans = fold_prep.transform(sample_x)
        if model_family == "LogisticRegression":
            fold_margin = fold_clf.decision_function(x_trans)
        else:
            dmat = xgb.DMatrix(x_trans, feature_names=explainer.feature_names)
            fold_margin = fold_clf.get_booster().predict(dmat, output_margin=True)
        fold_margins.append(fold_margin)

    expected_margin = np.mean(fold_margins, axis=0)

    # Property 1: Exact additivity to average uncalibrated margin
    assert np.allclose(reconstructed_margin, expected_margin, atol=1e-5)

    # Property 2: Non-equivalence to final calibrated probability
    calibrated_proba = cal_pipe.predict_proba(sample_x)[:, 1]
    sigmoid_reconstructed = expit(reconstructed_margin)
    logit_calibrated = logit(calibrated_proba)

    prob_diff = np.abs(sigmoid_reconstructed - calibrated_proba)
    logit_diff = np.abs(reconstructed_margin - logit_calibrated)

    # Across 10 samples, calibration mapping produces distinct probabilities from raw sigmoid
    assert np.any(prob_diff > 1e-4), "Sigmoid of raw SHAP sum should not equal calibrated probability"
    assert np.any(logit_diff > 1e-4), "Raw SHAP sum should not equal logit of calibrated probability"

    # Property 3: Explanation space contract
    assert explainer.explanation_space == "log-odds (model score)"


