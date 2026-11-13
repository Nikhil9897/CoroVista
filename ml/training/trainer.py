"""
CoroVista - Model Training & Artifact Serialization Service
Stage 2: Machine Learning Foundation

Responsible for:
1. Training the selected final pipeline for each target on the full dataset.
2. Saving complete, self-contained pipeline bundles:
   - models/cad/
   - models/lad/
   - models/lcx/
   - models/rca/
3. Bundling full metadata: feature list, threshold, calibration method, CV performance summary.
4. Providing deterministic model loading and inference verification.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

from ml.preprocessing.feature_metadata import assert_no_target_leakage
from ml.preprocessing.pipeline import build_preprocessing_pipeline, extract_features_and_targets
from ml.training.benchmark import DynamicScalePosWeightXGBClassifier

logger = logging.getLogger("corovista_trainer")

MODEL_DIR_MAP = {
    "Cath": Path("models/cad"),
    "LAD": Path("models/lad"),
    "LCX": Path("models/lcx"),
    "RCA": Path("models/rca"),
}


def create_final_pipeline(
    model_family: str,
    vhd_encoding: str = "onehot",
    scaler_type: str = "none",
    drop_rwma: bool = False,
    drop_bmi: bool = False,
    scale_pos_weight: float = 1.0,
    calibration_method: Optional[str] = None,
    random_state: int = 42,
    cv: Optional[Union[int, Any]] = None,
    y: Optional[Union[pd.Series, np.ndarray, List[int]]] = None,
) -> Union[Pipeline, CalibratedClassifierCV]:
    """
    Instantiates a full end-to-end pipeline (preprocessing + estimator/calibrator).

    When calibration is enabled:
    - Preprocessing and classifier are encapsulated in a Pipeline.
    - The complete Pipeline is passed to CalibratedClassifierCV so preprocessing
      and XGBoost class weighting are fitted independently inside every calibration partition.
    - If minority class count in y is < 2, falls back safely to an uncalibrated Pipeline.
    """
    # 1. Base preprocessing
    prep_pipe = build_preprocessing_pipeline(
        vhd_encoding=vhd_encoding,  # type: ignore
        scaler_type=scaler_type,  # type: ignore
        drop_rwma=drop_rwma,
        drop_bmi=drop_bmi,
    )

    # 2. Estimator instantiation
    if model_family == "LogisticRegression":
        estimator = LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=1.0,
            solver="liblinear",
            random_state=random_state,
        )
    elif model_family == "RandomForest":
        estimator = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )
    elif model_family == "XGBoost":
        estimator = DynamicScalePosWeightXGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        )
    else:
        raise ValueError(f"Unsupported model family: {model_family}")

    # 3. Base pipeline combining preprocessing and classifier
    base_pipeline = Pipeline([
        ("preprocessing", prep_pipe),
        ("classifier", estimator),
    ])

    # 4. Optional calibration wrapper
    if calibration_method in ["sigmoid", "isotonic"]:
        if y is not None:
            y_arr = np.asarray(y)
            unique_classes, class_counts = np.unique(y_arr, return_counts=True)
            min_class_count = int(np.min(class_counts)) if len(unique_classes) >= 2 else 0
            if min_class_count < 2:
                logger.warning(
                    "Insufficient minority class count (%d < 2) for %s calibration; "
                    "falling back to uncalibrated pipeline.",
                    min_class_count,
                    calibration_method,
                )
                return base_pipeline

            cal_splits = min(3, min_class_count) if cv is None else cv
        else:
            cal_splits = 3 if cv is None else cv

        if isinstance(cal_splits, int):
            cal_cv = StratifiedKFold(n_splits=cal_splits, shuffle=True, random_state=random_state)
        else:
            cal_cv = cal_splits

        return CalibratedClassifierCV(
            estimator=base_pipeline,
            method=calibration_method,
            cv=cal_cv,
        )

    return base_pipeline


def train_and_save_final_model(
    target_name: str,
    df_raw: pd.DataFrame,
    model_config: Dict[str, Any],
    cv_summary_metrics: Dict[str, Any],
    output_dir: Optional[Path] = None,
    random_state: int = 42,
) -> Path:
    """
    Fits the final pipeline on all available data and serializes
    the pipeline bundle and its audit metadata.
    """
    save_dir = output_dir or MODEL_DIR_MAP[target_name]
    save_dir.mkdir(parents=True, exist_ok=True)

    X, targets = extract_features_and_targets(df_raw)
    y = targets[target_name]

    # Positive class count preserved for audit metadata
    n_pos = int(y.sum())

    pipeline = create_final_pipeline(
        model_family=model_config["model_family"],
        vhd_encoding=model_config.get("vhd_encoding", "onehot"),
        scaler_type=model_config.get("scaler_type", "none"),
        drop_rwma=model_config.get("drop_rwma", False),
        drop_bmi=model_config.get("drop_bmi", False),
        scale_pos_weight=model_config.get("scale_pos_weight", 1.0),
        calibration_method=model_config.get("calibration_method", None),
        random_state=random_state,
        cv=model_config.get("cv", None),
        y=y,
    )

    # Train pipeline
    pipeline.fit(X, y)

    # Save pipeline binary artifact
    model_path = save_dir / "pipeline.joblib"
    joblib.dump(pipeline, model_path)

    # Record calibration method accurately (handles fallback to uncalibrated)
    if isinstance(pipeline, CalibratedClassifierCV):
        actual_calibration = model_config.get("calibration_method", "uncalibrated")
    else:
        actual_calibration = "uncalibrated"

    # Save metadata JSON
    metadata = {
        "target": target_name,
        "model_family": model_config["model_family"],
        "vhd_encoding": model_config.get("vhd_encoding", "onehot"),
        "scaler_type": model_config.get("scaler_type", "none"),
        "drop_rwma": model_config.get("drop_rwma", False),
        "drop_bmi": model_config.get("drop_bmi", False),
        "calibration_method": actual_calibration,
        "decision_threshold": model_config.get("decision_threshold", 0.5),
        "random_state": random_state,
        "training_samples": len(X),
        "training_positives": n_pos,
        "input_features": X.columns.tolist(),
        "cross_validation_metrics": cv_summary_metrics,
    }

    metadata_path = save_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return save_dir


def load_target_model(target_name: str) -> Tuple[Union[Pipeline, CalibratedClassifierCV], Dict[str, Any]]:
    """Loads a serialized final model pipeline and metadata."""
    target_dir = MODEL_DIR_MAP[target_name]
    model_path = target_dir / "pipeline.joblib"
    metadata_path = target_dir / "metadata.json"

    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found at {model_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Model metadata not found at {metadata_path}")

    pipeline = joblib.load(model_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return pipeline, metadata


def predict_patient(
    patient_df: pd.DataFrame,
) -> Dict[str, Dict[str, Union[float, str, int]]]:
    """
    Computes vessel risk probabilities and classifications across all 4 targets.
    Enforces strict leakage check on inference input.
    """
    assert_no_target_leakage(patient_df.columns.tolist())

    results = {}
    for target_name in ["Cath", "LAD", "LCX", "RCA"]:
        pipeline, metadata = load_target_model(target_name)
        thresh = metadata.get("decision_threshold", 0.5)

        prob = float(pipeline.predict_proba(patient_df)[0, 1])
        pred_int = int(prob >= thresh)

        label_map = {
            "Cath": {1: "CAD", 0: "Normal"},
            "LAD": {1: "Stenotic", 0: "Normal"},
            "LCX": {1: "Stenotic", 0: "Normal"},
            "RCA": {1: "Stenotic", 0: "Normal"},
        }

        results[target_name] = {
            "probability": round(prob, 4),
            "predicted_class_int": pred_int,
            "predicted_label": label_map[target_name][pred_int],
            "threshold_used": thresh,
            "model_family": metadata["model_family"],
        }

    return results
