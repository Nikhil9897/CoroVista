"""
CoroVista - Phase 4 Research Cross-Validation Protocol
Reusable, leakage-safe 5x5 Repeated Stratified K-Fold validation engine.

Guarantees:
1. Zero test-partition leakage: Preprocessing, scaling, imputation, class weighting,
   and calibration are fitted strictly inside outer training partitions.
2. Background for LinearExplainer is strictly restricted to the outer training partition.
3. TreeSHAP uses exact margin contributions from models trained only on training partitions.
4. Numerical reconstruction verification on every fold test sample.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold

from ml.preprocessing.pipeline import build_preprocessing_pipeline, extract_features_and_targets
from ml.training.benchmark import (
    DynamicScalePosWeightXGBClassifier,
    _build_and_fit_fold_model,
    _extract_positive_probs,
)

logger = logging.getLogger("corovista_research.cv_protocol")

# Target Configurations approved from Phase 3
APPROVED_TARGET_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Cath": {
        "target_name": "Cath",
        "clinical_name": "Overall CAD Status",
        "model_family": "XGBoost",
        "vhd_encoding": "onehot",
        "scaler_type": "none",
        "drop_rwma": False,
        "drop_bmi": False,
        "calibration_method": "sigmoid",
        "decision_threshold": 0.50,
    },
    "LAD": {
        "target_name": "LAD",
        "clinical_name": "Left Anterior Descending Stenosis",
        "model_family": "XGBoost",
        "vhd_encoding": "onehot",
        "scaler_type": "none",
        "drop_rwma": False,
        "drop_bmi": False,
        "calibration_method": "sigmoid",
        "decision_threshold": 0.50,
    },
    "LCX": {
        "target_name": "LCX",
        "clinical_name": "Left Circumflex Stenosis",
        "model_family": "XGBoost",
        "vhd_encoding": "onehot",
        "scaler_type": "none",
        "drop_rwma": False,
        "drop_bmi": False,
        "calibration_method": None,
        "decision_threshold": 0.50,
    },
    "RCA": {
        "target_name": "RCA",
        "clinical_name": "Right Coronary Artery Stenosis",
        "model_family": "LogisticRegression",
        "vhd_encoding": "onehot",
        "scaler_type": "standard",
        "drop_rwma": False,
        "drop_bmi": False,
        "calibration_method": "sigmoid",
        "decision_threshold": 0.35,
    },
}


def get_base_estimator(model_family: str, random_state: int = 42) -> Any:
    """Instantiates the base estimator with reproducible parameters."""
    if model_family == "LogisticRegression":
        return LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=1.0,
            solver="liblinear",
            random_state=random_state,
        )
    elif model_family == "XGBoost":
        return DynamicScalePosWeightXGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        )
    raise ValueError(f"Unsupported model family: {model_family}")


def extract_feature_names_from_prep(prep_pipe: Any) -> List[str]:
    """Extracts output feature names from a fitted preprocessing pipeline."""
    if hasattr(prep_pipe, "named_steps") and "processor" in prep_pipe.named_steps:
        proc = prep_pipe.named_steps["processor"]
        if hasattr(proc, "get_feature_names_out"):
            return list(proc.get_feature_names_out())
    if hasattr(prep_pipe, "get_feature_names_out"):
        return list(prep_pipe.get_feature_names_out())
    raise ValueError("Cannot extract feature names from preprocessing pipeline.")


def _align_shap_to_canonical(
    fold_shap: np.ndarray,
    fold_feature_names: List[str],
    canonical_feature_names: List[str],
) -> np.ndarray:
    """Aligns fold-specific SHAP attribution array to canonical feature ordering."""
    if fold_feature_names == canonical_feature_names:
        return fold_shap
    n_samples = len(fold_shap)
    aligned = np.zeros((n_samples, len(canonical_feature_names)), dtype=float)
    fold_name_to_idx = {name: idx for idx, name in enumerate(fold_feature_names)}
    for c_idx, c_name in enumerate(canonical_feature_names):
        if c_name in fold_name_to_idx:
            aligned[:, c_idx] = fold_shap[:, fold_name_to_idx[c_name]]
    return aligned


def compute_fold_shap(
    fitted_model: Any,
    model_family: str,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    feature_names: List[str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes exact SHAP attributions, base values, and raw model scores for outer test samples.

    Guarantees:
    - Background data for linear explainers is strictly restricted to X_train.
    - XGBoost uses exact C++ TreeSHAP margins.
    - CalibratedClassifierCV attributions are averaged across internal calibration estimators.
    - Attributions are consistently aligned to canonical feature names and ordering.

    Returns:
    - shap_values: shape (n_test, n_canonical_features)
    - base_values: shape (n_test,)
    - raw_scores: shape (n_test,)
    """
    n_test = len(X_test)

    if model_family == "XGBoost":
        if isinstance(fitted_model, CalibratedClassifierCV) or hasattr(fitted_model, "calibrated_classifiers_"):
            cal_clfs = fitted_model.calibrated_classifiers_
            contribs_list = []
            base_list = []
            direct_margins = []
            for cal in cal_clfs:
                fold_prep = cal.estimator.named_steps["preprocessing"]
                fold_clf = cal.estimator.named_steps["classifier"]
                fold_feat_names = extract_feature_names_from_prep(fold_prep)
                X_te_trans = fold_prep.transform(X_test)
                dmat = xgb.DMatrix(X_te_trans, feature_names=fold_feat_names)
                contribs = fold_clf.get_booster().predict(dmat, pred_contribs=True)

                aligned_shap = _align_shap_to_canonical(contribs[:, :-1], fold_feat_names, feature_names)
                contribs_list.append(aligned_shap)
                base_list.append(contribs[:, -1])
                direct_margins.append(fold_clf.get_booster().predict(dmat, output_margin=True))

            shap_values = np.mean(contribs_list, axis=0)
            base_values = np.mean(base_list, axis=0)
            raw_scores = np.mean(direct_margins, axis=0)
            return shap_values, base_values, raw_scores
        else:
            prep = fitted_model.named_steps["preprocessing"]
            clf = fitted_model.named_steps["classifier"]
            fold_feat_names = extract_feature_names_from_prep(prep)
            X_te_trans = prep.transform(X_test)
            dmat = xgb.DMatrix(X_te_trans, feature_names=fold_feat_names)
            contribs = clf.get_booster().predict(dmat, pred_contribs=True)
            shap_values = _align_shap_to_canonical(contribs[:, :-1], fold_feat_names, feature_names)
            base_values = contribs[:, -1]
            raw_scores = clf.get_booster().predict(dmat, output_margin=True)
            return shap_values, base_values, raw_scores

    elif model_family == "LogisticRegression":
        if isinstance(fitted_model, CalibratedClassifierCV) or hasattr(fitted_model, "calibrated_classifiers_"):
            cal_clfs = fitted_model.calibrated_classifiers_
            shap_list = []
            base_list = []
            score_list = []
            for cal in cal_clfs:
                fold_prep = cal.estimator.named_steps["preprocessing"]
                fold_clf = cal.estimator.named_steps["classifier"]
                fold_feat_names = extract_feature_names_from_prep(fold_prep)
                X_tr_trans = fold_prep.transform(X_train)  # Strict training background
                X_te_trans = fold_prep.transform(X_test)
                explainer = shap.LinearExplainer(fold_clf, X_tr_trans)
                s_vals = explainer.shap_values(X_te_trans)
                aligned_shap = _align_shap_to_canonical(s_vals, fold_feat_names, feature_names)
                shap_list.append(aligned_shap)
                b_val = float(explainer.expected_value)
                base_list.append(np.full(n_test, b_val))
                score_list.append(fold_clf.decision_function(X_te_trans))

            avg_shap = np.mean(shap_list, axis=0)
            avg_base = np.mean(base_list, axis=0)
            avg_scores = np.mean(score_list, axis=0)
            return avg_shap, avg_base, avg_scores
        else:
            prep = fitted_model.named_steps["preprocessing"]
            clf = fitted_model.named_steps["classifier"]
            fold_feat_names = extract_feature_names_from_prep(prep)
            X_tr_trans = prep.transform(X_train)
            X_te_trans = prep.transform(X_test)
            explainer = shap.LinearExplainer(clf, X_tr_trans)
            shap_values = explainer.shap_values(X_te_trans)
            aligned_shap = _align_shap_to_canonical(shap_values, fold_feat_names, feature_names)
            base_val = float(explainer.expected_value)
            base_values = np.full(n_test, base_val)
            raw_scores = clf.decision_function(X_te_trans)
            return aligned_shap, base_values, raw_scores

    raise NotImplementedError(f"Unsupported model family: {model_family}")


@dataclass
class TargetCVArtifacts:
    target_name: str
    clinical_name: str
    model_family: str
    decision_threshold: float
    calibration_method: Optional[str]
    feature_names: List[str]
    # DataFrames and Arrays
    oof_predictions_df: pd.DataFrame
    oof_shap_matrix: np.ndarray  # Shape: (n_patients, n_repeats, n_features)
    fold_summaries: List[Dict[str, Any]]
    fold_feature_importances: pd.DataFrame  # Rows: 25 folds, Columns: 57 features
    fold_feature_ranks: pd.DataFrame  # Rows: 25 folds, Columns: 57 features (1=top)
    reconstruction_all_passed: bool
    max_reconstruction_diff: float
    fold_models: List[Any] = field(default_factory=list)


def run_target_cv_experiment(
    target_name: str,
    df_raw: pd.DataFrame,
    n_splits: int = 5,
    n_repeats: int = 5,
    random_state: int = 42,
    config_override: Optional[Dict[str, Any]] = None,
) -> TargetCVArtifacts:
    """
    Executes the 5x5 Repeated Stratified K-Fold evaluation for a single target,
    collecting out-of-fold predictions, exact SHAP attributions, and reconstruction audits.
    """
    config = dict(APPROVED_TARGET_CONFIGS[target_name])
    if config_override:
        config.update(config_override)

    X, targets = extract_features_and_targets(df_raw)
    y = targets[target_name]
    y_arr = np.asarray(y)

    model_family = config["model_family"]
    scaler_type = config["scaler_type"]
    vhd_encoding = config["vhd_encoding"]
    drop_rwma = config["drop_rwma"]
    drop_bmi = config["drop_bmi"]
    calibration_method = config["calibration_method"]
    decision_threshold = float(config["decision_threshold"])

    rskf = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
    )

    n_patients = len(X)
    full_prep = build_preprocessing_pipeline(
        vhd_encoding=vhd_encoding, scaler_type=scaler_type, drop_rwma=drop_rwma, drop_bmi=drop_bmi
    ).fit(X)
    canonical_feature_names = extract_feature_names_from_prep(full_prep)
    n_features = len(canonical_feature_names)
    oof_shap_tensor = np.full((n_patients, n_repeats, n_features), np.nan, dtype=float)

    oof_records: List[Dict[str, Any]] = []
    fold_summaries: List[Dict[str, Any]] = []
    fold_importances_list: List[np.ndarray] = []
    fold_models: List[Any] = []

    global_max_reconstruction_diff = 0.0
    all_reconstruction_passed = True

    for outer_fold_idx, (train_idx, test_idx) in enumerate(rskf.split(X, y)):
        repeat_idx = outer_fold_idx // n_splits
        split_idx = outer_fold_idx % n_splits
        fold_seed = random_state + outer_fold_idx

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        base_estimator = get_base_estimator(model_family, random_state=fold_seed)

        fitted_model = _build_and_fit_fold_model(
            X_fit=X_train,
            y_fit=y_train,
            model_name=model_family,
            base_estimator=base_estimator,
            vhd_encoding=vhd_encoding,
            scaler_type=scaler_type,
            drop_rwma=drop_rwma,
            drop_bmi=drop_bmi,
            calibration_method=calibration_method,
            seed=fold_seed,
        )
        fold_models.append(fitted_model)

        # 1. Continuous probabilities and discrete classifications
        p_test = _extract_positive_probs(fitted_model, X_test)
        y_pred = (p_test >= decision_threshold).astype(int)

        # 2. SHAP attributions and raw model scores
        shap_vals, base_vals, raw_scores = compute_fold_shap(
            fitted_model=fitted_model,
            model_family=model_family,
            X_train=X_train,
            X_test=X_test,
            feature_names=canonical_feature_names,
        )

        # 3. Numerical reconstruction verification
        reconstructed = np.sum(shap_vals, axis=1) + base_vals
        reconstruction_diffs = np.abs(reconstructed - raw_scores)
        fold_max_diff = float(np.max(reconstruction_diffs))
        if fold_max_diff > global_max_reconstruction_diff:
            global_max_reconstruction_diff = fold_max_diff
        fold_passed = fold_max_diff < 1e-4
        if not fold_passed:
            all_reconstruction_passed = False
            logger.warning(
                "Fold %d (%s) failed reconstruction check: max diff = %.6e",
                outer_fold_idx,
                target_name,
                fold_max_diff,
            )

        # 4. Fold-level feature importance (mean absolute SHAP across outer test partition)
        fold_mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
        fold_importances_list.append(fold_mean_abs_shap)

        fold_summaries.append({
            "outer_fold_idx": outer_fold_idx,
            "repeat_idx": repeat_idx,
            "split_idx": split_idx,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "n_test_positives": int(np.sum(y_test == 1)),
            "reconstruction_max_diff": fold_max_diff,
            "reconstruction_passed": fold_passed,
        })

        # 5. Record patient out-of-fold predictions and SHAP
        for i_local, pt_idx in enumerate(test_idx):
            oof_shap_tensor[pt_idx, repeat_idx, :] = shap_vals[i_local]
            oof_records.append({
                "patient_idx": int(pt_idx),
                "repeat_idx": int(repeat_idx),
                "split_idx": int(split_idx),
                "outer_fold_idx": int(outer_fold_idx),
                "y_true": int(y_arr[pt_idx]),
                "prob": float(p_test[i_local]),
                "pred": int(y_pred[i_local]),
                "raw_score": float(raw_scores[i_local]),
                "base_value": float(base_vals[i_local]),
                "reconstruction_diff": float(reconstruction_diffs[i_local]),
            })

    oof_df = pd.DataFrame(oof_records).sort_values(by=["patient_idx", "repeat_idx"]).reset_index(drop=True)
    fold_imp_df = pd.DataFrame(fold_importances_list, columns=canonical_feature_names)

    # Rank features per fold: 1 = highest importance (descending order of importance)
    fold_ranks_df = fold_imp_df.rank(axis=1, ascending=False, method="min")

    return TargetCVArtifacts(
        target_name=target_name,
        clinical_name=config["clinical_name"],
        model_family=model_family,
        decision_threshold=decision_threshold,
        calibration_method=calibration_method,
        feature_names=canonical_feature_names or [],
        oof_predictions_df=oof_df,
        oof_shap_matrix=oof_shap_tensor,
        fold_summaries=fold_summaries,
        fold_feature_importances=fold_imp_df,
        fold_feature_ranks=fold_ranks_df,
        reconstruction_all_passed=all_reconstruction_passed,
        max_reconstruction_diff=global_max_reconstruction_diff,
        fold_models=fold_models,
    )
