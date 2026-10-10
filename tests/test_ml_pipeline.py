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

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.preprocessing.feature_metadata import (
    ELIGIBLE_FEATURES,
    FEATURE_REGISTRY,
    TARGET_COLUMNS,
    ZERO_VARIANCE_COLUMNS,
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
from ml.training.trainer import (
    create_final_pipeline,
    load_target_model,
    predict_patient,
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
