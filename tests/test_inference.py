"""
CoroVista - Multi-Target Inference Unit & Integration Tests

Tests:
1. Model loading & pipeline integrity
2. Multi-target prediction contracts & schema compliance
3. Probability bounds [0, 1] & threshold logic (including RCA threshold 0.38)
4. Determinism of repeated inference
5. Missing feature rejection
6. Unexpected/malformed categorical input rejection
7. Categorical normalization ('Fmale', VHD casing)
8. Strict target leakage prevention (rejecting 'Cath', 'LAD', 'LCX', 'RCA')
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.corovista.inference.loader import load_all_models, load_model_pipeline, clear_model_cache
from src.corovista.inference.predictor import predict_patient
from src.corovista.inference.schemas import PatientInferenceResponse, TargetPrediction
from src.corovista.inference.validation import validate_and_normalize_patient_input
from ml.preprocessing.pipeline import load_dataset, extract_features_and_targets

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")


@pytest.fixture(scope="session")
def sample_patient_dict():
    """Returns a valid patient dictionary from raw dataset row 0."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, _ = extract_features_and_targets(df_raw)
    return X_raw.iloc[0].to_dict()


# 1. Model Loading
def test_load_all_models():
    clear_model_cache()
    models = load_all_models()
    assert set(models.keys()) == {"cath", "lad", "lcx", "rca"}

    # Verify thresholds
    assert models["cath"]["threshold"] == 0.50
    assert models["lad"]["threshold"] == 0.50
    assert models["lcx"]["threshold"] == 0.50
    assert models["rca"]["threshold"] == 0.38

    # Verify model families
    assert models["cath"]["model_family"] == "XGBoost"
    assert models["lad"]["model_family"] == "XGBoost"
    assert models["lcx"]["model_family"] == "XGBoost"
    assert models["rca"]["model_family"] == "LogisticRegression"


def test_load_invalid_target():
    with pytest.raises(ValueError, match="Unknown target"):
        load_model_pipeline("invalid_target")


# 2. Prediction Schema & Probability Bounds
def test_predict_patient_schema(sample_patient_dict):
    res = predict_patient(sample_patient_dict)
    assert isinstance(res, PatientInferenceResponse)

    for target_name in ["cath", "lad", "lcx", "rca"]:
        pred: TargetPrediction = getattr(res, target_name)
        assert 0.0 <= pred.probability <= 1.0
        assert pred.prediction in ["CAD", "Normal", "Stenotic"]
        assert 0.0 <= pred.threshold <= 1.0


def test_predict_patient_dict_format(sample_patient_dict):
    dict_res = predict_patient(sample_patient_dict, return_dict=True)
    assert isinstance(dict_res, dict)
    assert set(dict_res.keys()) == {"cath", "lad", "lcx", "rca"}
    for t in dict_res.values():
        assert "probability" in t
        assert "prediction" in t
        assert "threshold" in t


# 3. Threshold Separation
def test_threshold_separation(sample_patient_dict):
    res = predict_patient(sample_patient_dict)
    # RCA has calibrated threshold of 0.38
    assert res.rca.threshold == 0.38
    if res.rca.probability >= 0.38:
        assert res.rca.prediction == "Stenotic"
    else:
        assert res.rca.prediction == "Normal"


# 4. Determinism
def test_inference_determinism(sample_patient_dict):
    res1 = predict_patient(sample_patient_dict, return_dict=True)
    res2 = predict_patient(sample_patient_dict, return_dict=True)
    assert res1 == res2


# 5. Missing Feature Rejection
def test_missing_feature_rejection(sample_patient_dict):
    broken_dict = dict(sample_patient_dict)
    del broken_dict["Age"]
    with pytest.raises(ValueError, match="Missing required clinical feature"):
        predict_patient(broken_dict)


# 6. Categorical Normalization
def test_categorical_normalization(sample_patient_dict):
    norm_dict = dict(sample_patient_dict)
    norm_dict["Sex"] = "Fmale"
    norm_dict["VHD"] = "mild"
    clean_df = validate_and_normalize_patient_input(norm_dict)
    assert clean_df["Sex"].iloc[0] == "Female"
    assert clean_df["VHD"].iloc[0] == "Mild"

    res = predict_patient(norm_dict)
    assert res.cath.probability is not None


# 7. Invalid Categorical Rejection
def test_invalid_categorical_rejection(sample_patient_dict):
    bad_dict = dict(sample_patient_dict)
    bad_dict["Sex"] = "UnknownGender"
    with pytest.raises(ValueError, match="Invalid value for 'Sex'"):
        predict_patient(bad_dict)

    bad_dict2 = dict(sample_patient_dict)
    bad_dict2["VHD"] = "ExtremelySevere"
    with pytest.raises(ValueError, match="Invalid value for 'VHD'"):
        predict_patient(bad_dict2)


# 8. Strict Target Leakage Rejection
def test_target_leakage_rejection(sample_patient_dict):
    for target_col in ["Cath", "LAD", "LCX", "RCA", "cath", "lad"]:
        leaked_input = dict(sample_patient_dict)
        leaked_input[target_col] = "Normal"
        with pytest.raises(ValueError, match="TARGET LEAKAGE DETECTED"):
            predict_patient(leaked_input)
