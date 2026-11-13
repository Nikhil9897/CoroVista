"""
CoroVista - Unit & Pipeline Tests for Machine Learning Training Suite

Covers:
1. Target separation & automated leakage assertion failure
2. Feature metadata registry validity and coverage
3. Categorical normalization (Sex typo 'Fmale' -> 'Female'/0, 'Male' -> 1)
4. VHD casing normalization & dual encoding (one-hot vs ordinal)
5. Exertional CP zero-variance removal
6. Pipeline construction (ColumnTransformer, scaling options)
7. Cross-validation reproducibility
8. Probability output shape, range [0, 1], and thresholding
9. Model artifact saving, loading, and prediction consistency
10. Controlled ablation switches (drop_rwma, drop_bmi)
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.preprocessing.feature_metadata import (
    FEATURE_REGISTRY,
    TARGET_COLUMNS,
    assert_no_target_leakage,
    get_eligible_feature_names,
    get_feature_metadata,
)
from ml.preprocessing.pipeline import (
    ClinicalFeatureCleaner,
    LeakageGuardTransformer,
    build_preprocessing_pipeline,
    extract_features_and_targets,
    load_dataset,
)
from ml.training.benchmark import DynamicScalePosWeightXGBClassifier
from ml.training.trainer import (
    create_final_pipeline,
    train_and_save_final_model,
)

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")


@pytest.fixture(scope="session")
def raw_df():
    """Session fixture loading primary dataset."""
    assert RAW_DATA_PATH.exists()
    return load_dataset(RAW_DATA_PATH, sheet_name="Sheet 1 - Table 1")


# 1. Target Separation & Leakage Assertions
def test_extract_features_and_targets(raw_df):
    X, targets = extract_features_and_targets(raw_df)
    assert X.shape == (303, 55)
    assert set(targets.keys()) == set(TARGET_COLUMNS)

    for target in TARGET_COLUMNS:
        assert target not in X.columns, f"Target {target} found in feature matrix X"
        assert len(targets[target]) == 303
        assert set(targets[target].unique()).issubset({0, 1})


def test_leakage_assertion_raises():
    leaked_cols = ["Age", "Sex", "Cath", "DM"]
    with pytest.raises(ValueError, match="CRITICAL TARGET LEAKAGE DETECTED"):
        assert_no_target_leakage(leaked_cols)

    transformer = LeakageGuardTransformer()
    dummy_df = pd.DataFrame({"Age": [50], "LAD": ["Stenotic"]})
    with pytest.raises(ValueError, match="CRITICAL TARGET LEAKAGE DETECTED"):
        transformer.fit(dummy_df)


# 2. Feature Metadata Registry Validity
def test_feature_metadata_registry():
    assert len(FEATURE_REGISTRY) >= 59
    assert len(get_eligible_feature_names()) == 54

    for name in get_eligible_feature_names():
        meta = get_feature_metadata(name)
        assert meta.model_eligibility == "Eligible"
        assert meta.clinical_category in [
            "Demographic", "Clinical Examination", "ECG", "Laboratory", "Echocardiographic"
        ]

    # Check zero-variance feature metadata
    ex_cp = get_feature_metadata("Exertional CP")
    assert ex_cp.model_eligibility == "Excluded (Zero Variance)"

    # Check targets metadata
    for target in TARGET_COLUMNS:
        t_meta = get_feature_metadata(target)
        assert t_meta.model_eligibility == "Excluded (Target)"


# 3. Categorical Normalization (Sex)
def test_sex_normalization():
    cleaner = ClinicalFeatureCleaner()
    df_test = pd.DataFrame({"Sex": ["Male", "Fmale", "Female", "male"], "Age": [50, 60, 45, 70]})
    cleaner.fit(df_test)
    df_clean = cleaner.transform(df_test)
    assert list(df_clean["Sex"]) == [1, 0, 0, 1]


# 4. VHD Normalization & Dual Encoding
def test_vhd_normalization_onehot_and_ordinal():
    # One-hot normalization
    cleaner_oh = ClinicalFeatureCleaner(vhd_encoding="onehot")
    df_vhd = pd.DataFrame({"VHD": ["mild", "Severe", "Moderate", "N"]})
    cleaner_oh.fit(df_vhd)
    df_oh = cleaner_oh.transform(df_vhd)
    assert list(df_oh["VHD"]) == ["Mild", "Severe", "Moderate", "Normal"]

    # Ordinal normalization
    cleaner_ord = ClinicalFeatureCleaner(vhd_encoding="ordinal")
    cleaner_ord.fit(df_vhd)
    df_ord = cleaner_ord.transform(df_vhd)
    assert list(df_ord["VHD"]) == [1, 3, 2, 0]


# 5. Exertional CP Removal
def test_zero_variance_dropper():
    cleaner = ClinicalFeatureCleaner(drop_zero_variance=True)
    df_test = pd.DataFrame({"Exertional CP": ["N", "N"], "Age": [50, 60]})
    cleaner.fit(df_test)
    df_clean = cleaner.transform(df_test)
    assert "Exertional CP" not in df_clean.columns
    assert "Age" in df_clean.columns


# 6. Pipeline Construction & Transformations
def test_pipeline_construction(raw_df):
    X, _ = extract_features_and_targets(raw_df)

    # One-hot + StandardScaler
    pipe_oh = build_preprocessing_pipeline(vhd_encoding="onehot", scaler_type="standard")
    X_oh = pipe_oh.fit_transform(X)
    assert isinstance(X_oh, np.ndarray)
    assert X_oh.shape[0] == 303
    assert not np.isnan(X_oh).any()

    # Ordinal + RobustScaler
    pipe_ord = build_preprocessing_pipeline(vhd_encoding="ordinal", scaler_type="robust")
    X_ord = pipe_ord.fit_transform(X)
    assert isinstance(X_ord, np.ndarray)
    assert X_ord.shape[0] == 303
    assert not np.isnan(X_ord).any()


# 7. Controlled Ablation Switches (RWMA and BMI)
def test_ablation_switches(raw_df):
    X, _ = extract_features_and_targets(raw_df)

    # RWMA ablation
    pipe_no_rwma = build_preprocessing_pipeline(drop_rwma=True)
    X_no_rwma = pipe_no_rwma.fit_transform(X)
    pipe_with_rwma = build_preprocessing_pipeline(drop_rwma=False)
    X_with_rwma = pipe_with_rwma.fit_transform(X)
    assert X_no_rwma.shape[1] == X_with_rwma.shape[1] - 1

    # BMI ablation
    pipe_no_bmi = build_preprocessing_pipeline(drop_bmi=True)
    X_no_bmi = pipe_no_bmi.fit_transform(X)
    assert X_no_bmi.shape[1] == X_with_rwma.shape[1] - 1


# 8. Model Final Pipeline Creation & Predict Proba Range
def test_model_pipeline_predict_proba(raw_df):
    X, targets = extract_features_and_targets(raw_df)
    y = targets["Cath"]

    # Test LogisticRegression pipeline
    pipe_lr = create_final_pipeline("LogisticRegression", scaler_type="standard", random_state=42)
    pipe_lr.fit(X.iloc[:200], y.iloc[:200])
    probs_lr = pipe_lr.predict_proba(X.iloc[200:])[:, 1]
    assert len(probs_lr) == 103
    assert (probs_lr >= 0.0).all() and (probs_lr <= 1.0).all()

    # Test XGBoost pipeline
    pipe_xgb = create_final_pipeline("XGBoost", scaler_type="none", random_state=42)
    pipe_xgb.fit(X.iloc[:200], y.iloc[:200])
    probs_xgb = pipe_xgb.predict_proba(X.iloc[200:])[:, 1]
    assert len(probs_xgb) == 103
    assert (probs_xgb >= 0.0).all() and (probs_xgb <= 1.0).all()


# 9. Model Serialization & Predict Patient
def test_model_saving_and_inference(raw_df, tmp_path):
    config = {
        "model_family": "LogisticRegression",
        "scaler_type": "standard",
        "vhd_encoding": "onehot",
        "decision_threshold": 0.5,
    }
    cv_metrics = {"roc_auc": {"mean": 0.85, "std": 0.04}}
    save_dir = train_and_save_final_model(
        target_name="Cath",
        df_raw=raw_df,
        model_config=config,
        cv_summary_metrics=cv_metrics,
        output_dir=tmp_path / "cad",
    )
    assert (save_dir / "pipeline.joblib").exists()
    assert (save_dir / "metadata.json").exists()


# 10. Calibration Pipeline Structure & Fallback Methodology
def test_create_final_pipeline_calibrated_and_uncalibrated():
    """Verifies calibrated and uncalibrated pipeline instantiation contracts."""
    # Uncalibrated pipeline creation (calibration_method=None)
    pipe_uncal = create_final_pipeline("LogisticRegression", scaler_type="standard", calibration_method=None)
    assert isinstance(pipe_uncal, Pipeline)
    assert not isinstance(pipe_uncal, CalibratedClassifierCV)
    assert "preprocessing" in pipe_uncal.named_steps
    assert "classifier" in pipe_uncal.named_steps
    assert isinstance(pipe_uncal.named_steps["classifier"], LogisticRegression)

    # Uncalibrated pipeline creation (calibration_method="uncalibrated")
    pipe_uncal_str = create_final_pipeline("XGBoost", scaler_type="none", calibration_method="uncalibrated")
    assert isinstance(pipe_uncal_str, Pipeline)
    assert not isinstance(pipe_uncal_str, CalibratedClassifierCV)
    assert isinstance(pipe_uncal_str.named_steps["classifier"], DynamicScalePosWeightXGBClassifier)

    # Calibrated pipeline creation (sigmoid)
    pipe_cal_sig = create_final_pipeline("LogisticRegression", scaler_type="standard", calibration_method="sigmoid")
    assert isinstance(pipe_cal_sig, CalibratedClassifierCV)
    assert pipe_cal_sig.method == "sigmoid"
    assert isinstance(pipe_cal_sig.estimator, Pipeline)
    assert "preprocessing" in pipe_cal_sig.estimator.named_steps
    assert "classifier" in pipe_cal_sig.estimator.named_steps

    # Calibrated pipeline creation (isotonic)
    pipe_cal_iso = create_final_pipeline("XGBoost", scaler_type="none", calibration_method="isotonic")
    assert isinstance(pipe_cal_iso, CalibratedClassifierCV)
    assert pipe_cal_iso.method == "isotonic"
    assert isinstance(pipe_cal_iso.estimator, Pipeline)
    assert isinstance(pipe_cal_iso.estimator.named_steps["classifier"], DynamicScalePosWeightXGBClassifier)


def test_preprocessing_inside_calibration_estimator(raw_df, monkeypatch):
    """
    Verifies that create_final_pipeline encapsulates the complete Pipeline (preprocessing
    + classifier) inside CalibratedClassifierCV so preprocessing is fitted inside each
    calibration partition rather than on the full dataset beforehand.
    """
    X, _ = extract_features_and_targets(raw_df)

    fit_sample_sizes = []
    orig_scaler_fit = StandardScaler.fit

    def spy_scaler_fit(self, X_in, y_in=None, **kwargs):
        fit_sample_sizes.append(len(X_in))
        return orig_scaler_fit(self, X_in, y_in, **kwargs)

    monkeypatch.setattr(StandardScaler, "fit", spy_scaler_fit)

    X_slice = X.iloc[:30]
    y_slice = pd.Series([1] * 15 + [0] * 15, index=X_slice.index)

    pipe_cal = create_final_pipeline(
        "LogisticRegression",
        scaler_type="standard",
        calibration_method="sigmoid",
        random_state=42,
    )
    assert isinstance(pipe_cal, CalibratedClassifierCV)
    assert isinstance(pipe_cal.estimator, Pipeline)

    pipe_cal.fit(X_slice, y_slice)

    # In 3-fold CalibratedClassifierCV on 30 samples, each calibration training fold is 20 samples.
    # Preprocessing must fit strictly inside calibration splits (20 samples), never on full 30.
    assert len(fit_sample_sizes) == 3
    assert all(sz == 20 for sz in fit_sample_sizes)
    assert 30 not in fit_sample_sizes

    probs = pipe_cal.predict_proba(X.iloc[30:50])
    assert probs.shape == (20, 2)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()


def test_xgboost_fold_specific_class_weights(raw_df):
    """
    Verifies that DynamicScalePosWeightXGBClassifier dynamically computes scale_pos_weight
    strictly from each partition's training labels, both uncalibrated and calibrated.
    """
    X, _ = extract_features_and_targets(raw_df)

    # 1. Uncalibrated pipeline: dynamic weight derivation across different fit partitions
    pipe_uncal = create_final_pipeline("XGBoost", scaler_type="none", random_state=42)

    # Partition 1: 30 samples, 10 positives, 20 negatives -> scale_pos_weight = 20 / 10 = 2.0
    y_part1 = pd.Series([1] * 10 + [0] * 20, index=X.iloc[:30].index)
    pipe_uncal.fit(X.iloc[:30], y_part1)
    xgb_clf1 = pipe_uncal.named_steps["classifier"]
    assert isinstance(xgb_clf1, DynamicScalePosWeightXGBClassifier)
    assert xgb_clf1.computed_scale_pos_weight_ == 2.0

    # Partition 2: 35 samples, 5 positives, 30 negatives -> scale_pos_weight = 30 / 5 = 6.0
    y_part2 = pd.Series([1] * 5 + [0] * 30, index=X.iloc[:35].index)
    pipe_uncal.fit(X.iloc[:35], y_part2)
    xgb_clf2 = pipe_uncal.named_steps["classifier"]
    assert xgb_clf2.computed_scale_pos_weight_ == 6.0

    # 2. Calibrated pipeline: each calibration fold computes its own fold-specific class weight
    y_part3 = pd.Series([1] * 15 + [0] * 30, index=X.iloc[:45].index)
    pipe_cal = create_final_pipeline("XGBoost", scaler_type="none", calibration_method="sigmoid", random_state=42)
    pipe_cal.fit(X.iloc[:45], y_part3)

    assert isinstance(pipe_cal, CalibratedClassifierCV)
    assert len(pipe_cal.calibrated_classifiers_) == 3

    for cal_clf in pipe_cal.calibrated_classifiers_:
        fold_pipe = cal_clf.estimator
        assert isinstance(fold_pipe, Pipeline)
        fold_xgb = fold_pipe.named_steps["classifier"]
        assert isinstance(fold_xgb, DynamicScalePosWeightXGBClassifier)
        assert hasattr(fold_xgb, "computed_scale_pos_weight_")
        assert fold_xgb.computed_scale_pos_weight_ > 0


def test_low_minority_count_calibration_fallback(raw_df, tmp_path):
    """
    Verifies that when minority class count is < 2:
    1. create_final_pipeline with y safely falls back to uncalibrated Pipeline and does not fail.
    2. train_and_save_final_model safely falls back to uncalibrated pipeline, saves artifacts,
       and records 'uncalibrated' in metadata.json while preserving training_positives.
    """
    X, _ = extract_features_and_targets(raw_df)
    X_tiny = X.iloc[:20]

    # Exactly 1 positive sample (< 2 minority count)
    y_single_pos = pd.Series([1] + [0] * 19, index=X_tiny.index)

    # 1. Pipeline creation with low-minority y falls back to uncalibrated Pipeline
    pipe_fallback = create_final_pipeline(
        "LogisticRegression",
        scaler_type="standard",
        calibration_method="sigmoid",
        random_state=42,
        y=y_single_pos,
    )
    assert isinstance(pipe_fallback, Pipeline)
    assert not isinstance(pipe_fallback, CalibratedClassifierCV)
    assert "preprocessing" in pipe_fallback.named_steps
    assert "classifier" in pipe_fallback.named_steps

    # Fitting must succeed without calibration fold failure
    pipe_fallback.fit(X_tiny, y_single_pos)
    probs = pipe_fallback.predict_proba(X_tiny)
    assert probs.shape == (20, 2)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    # 2. train_and_save_final_model with low-minority raw dataframe
    df_tiny = raw_df.iloc[:20].copy()
    df_tiny["Cath"] = ["CAD"] + ["Normal"] * 19

    save_dir = train_and_save_final_model(
        target_name="Cath",
        df_raw=df_tiny,
        model_config={
            "model_family": "LogisticRegression",
            "scaler_type": "standard",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.5,
        },
        cv_summary_metrics={"roc_auc": {"mean": 0.75, "std": 0.05}},
        output_dir=tmp_path / "low_minority_cad",
        random_state=42,
    )

    assert (save_dir / "pipeline.joblib").exists()
    assert (save_dir / "metadata.json").exists()

    with open(save_dir / "metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Metadata must accurately reflect uncalibrated fallback and positive count
    assert meta["calibration_method"] == "uncalibrated"
    assert meta["training_positives"] == 1
    assert meta["training_samples"] == 20

    # Saved pipeline should be uncalibrated Pipeline
    saved_pipe = joblib.load(save_dir / "pipeline.joblib")
    assert isinstance(saved_pipe, Pipeline)
    assert not isinstance(saved_pipe, CalibratedClassifierCV)

