"""
CoroVista - Model Benchmarking & Validation Engine
Stage 2: Machine Learning Foundation

Conducts leakage-safe Repeated Stratified K-Fold Cross-Validation (internal validation):
- Default 5 Folds x 5 Repeats = 25 correlated fold evaluations on the same cohort
  (not 25 independent datasets and not external validation).
- Evaluates 4 baseline model families:
  1. DummyClassifier (Baseline)
  2. Logistic Regression (Linear)
  3. Random Forest (Bagging)
  4. XGBoost (Boosting)
- Benchmarks Preprocessing configurations:
  - Encoding: One-Hot vs Ordinal
  - Scaling: None vs StandardScaler vs RobustScaler
- Conducts Controlled Scientific Ablations:
  - RWMA Ablation: Model With vs Without 'Region RWMA'
  - Collinearity Ablation: Model With vs Without 'BMI'
- Evaluates Probability Calibration with Pipeline encapsulation inside CalibratedClassifierCV:
  - Uncalibrated vs Sigmoid (Platt) vs Isotonic
- Performs Inner Out-of-Fold (OOF) Threshold Optimization strictly within each outer
  training fold (outer test folds are never used for threshold selection, preprocessing,
  calibration, or class weighting).
"""

import copy
import functools
import logging
from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.evaluation.metrics import (
    _validate_threshold_metric,
    aggregate_cv_metrics,
    compute_metrics,
    find_optimal_threshold,
)
from ml.preprocessing.pipeline import build_preprocessing_pipeline, extract_features_and_targets

logger = logging.getLogger("corovista_benchmark")


class _ConstantBinaryClassifier(BaseEstimator, ClassifierMixin):
    """Fallback predictor used only when a training partition contains a single class."""

    def __init__(self, constant_class: int = 0):
        self.constant_class = int(constant_class)
        self.classes_ = np.array([0, 1], dtype=int)

    def fit(self, X: Any, y: Any = None) -> "_ConstantBinaryClassifier":
        if y is not None and len(y) > 0:
            self.constant_class = int(np.asarray(y)[0])
        self.classes_ = np.array([0, 1], dtype=int)
        return self

    def predict_proba(self, X: Any) -> np.ndarray:
        n = len(X)
        probs = np.zeros((n, 2), dtype=float)
        if self.constant_class == 1:
            probs[:, 1] = 1.0
        else:
            probs[:, 0] = 1.0
        return probs

    def predict(self, X: Any) -> np.ndarray:
        return np.full(len(X), self.constant_class, dtype=int)


def compute_scale_pos_weight(y_train: Union[pd.Series, np.ndarray, List[int]]) -> float:
    """
    Computes XGBoost `scale_pos_weight` (n_neg / n_pos) strictly from a training
    label partition. Safely returns 1.0 if either class has zero observations.
    """
    y_arr = np.asarray(y_train)
    n_pos = int(np.sum(y_arr == 1))
    n_neg = int(np.sum(y_arr == 0))
    if n_pos <= 0 or n_neg <= 0:
        return 1.0
    return float(round(n_neg / n_pos, 3))


class DynamicScalePosWeightXGBClassifier(XGBClassifier):
    """
    Clone-compatible XGBClassifier subclass that computes `scale_pos_weight`
    dynamically inside every `fit(X, y)` call strictly from the `y` labels
    received by that fit invocation.

    This prevents class-weight leakage across CalibratedClassifierCV internal
    calibration splits, inner OOF threshold-selection folds, and outer CV folds.
    """

    @functools.wraps(XGBClassifier.fit)
    def fit(self, X: Any, y: Any, **kwargs: Any) -> "DynamicScalePosWeightXGBClassifier":
        fold_pos_weight = compute_scale_pos_weight(y)
        orig_weight = self.scale_pos_weight
        self.scale_pos_weight = fold_pos_weight
        self.computed_scale_pos_weight_ = fold_pos_weight
        try:
            return super().fit(X, y, **kwargs)
        finally:
            self.scale_pos_weight = orig_weight


def get_model_instances(
    pos_weight: float = 1.0,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Instantiates the baseline model candidates with reproducible seeds.

    Note: XGBoost uses `DynamicScalePosWeightXGBClassifier`, which recomputes
    `scale_pos_weight` dynamically inside every `fit(X, y)` call strictly from
    that partition's training labels (never from outer test, full target, or
    calibration-validation labels).
    """
    return {
        "Dummy": DummyClassifier(strategy="prior"),
        "LogisticRegression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=1.0,
            random_state=random_state,
            solver="liblinear",
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "XGBoost": DynamicScalePosWeightXGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=pos_weight,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def _prepare_fold_estimator(
    base_estimator: Any,
    model_name: str,
) -> Any:
    """
    Clones/copies the estimator without inspecting any label vector.
    Any XGBClassifier instance is ensured to use `DynamicScalePosWeightXGBClassifier`
    so `scale_pos_weight` is derived inside each individual `fit(X, y)` call
    (including internal CalibratedClassifierCV splits).
    """
    model = copy.deepcopy(base_estimator)
    if (model_name == "XGBoost" or isinstance(model, XGBClassifier)) and isinstance(
        model, XGBClassifier
    ):
        if not isinstance(model, DynamicScalePosWeightXGBClassifier):
            model = DynamicScalePosWeightXGBClassifier(**model.get_params())
    return model


def _extract_positive_probs(fitted_estimator: Any, X_eval: pd.DataFrame) -> np.ndarray:
    """Extracts class-1 predicted probabilities safely across binary/single-class estimators."""
    if hasattr(fitted_estimator, "predict_proba"):
        probs = np.asarray(fitted_estimator.predict_proba(X_eval), dtype=float)
        if probs.ndim == 2:
            if hasattr(fitted_estimator, "classes_"):
                classes = list(fitted_estimator.classes_)
                if 1 in classes:
                    p1 = probs[:, classes.index(1)]
                else:
                    p1 = np.zeros(len(X_eval), dtype=float)
            elif probs.shape[1] > 1:
                p1 = probs[:, 1]
            else:
                p1 = probs[:, 0]
        else:
            p1 = probs
    else:
        p1 = np.asarray(fitted_estimator.predict(X_eval), dtype=float)

    return np.clip(p1, 0.0, 1.0)


def _build_and_fit_fold_model(
    X_fit: pd.DataFrame,
    y_fit: pd.Series,
    model_name: str,
    base_estimator: Any,
    vhd_encoding: Literal["onehot", "ordinal"],
    scaler_type: Literal["none", "standard", "robust"],
    drop_rwma: bool,
    drop_bmi: bool,
    calibration_method: Optional[Literal["sigmoid", "isotonic"]],
    seed: int,
) -> Any:
    """
    Constructs a full Pipeline(preprocessing, classifier), optionally wraps it in
    CalibratedClassifierCV so preprocessing and XGBoost class weighting are fitted
    independently inside every calibration partition, and fits strictly on (X_fit, y_fit).
    """
    y_arr = np.asarray(y_fit)
    unique_classes, class_counts = np.unique(y_arr, return_counts=True)

    if len(unique_classes) < 2:
        logger.warning(
            "Training partition for %s contains only class %s; using constant fallback predictor.",
            model_name,
            unique_classes.tolist(),
        )
        return _ConstantBinaryClassifier(constant_class=int(unique_classes[0])).fit(X_fit, y_fit)

    prep_pipe = build_preprocessing_pipeline(
        vhd_encoding=vhd_encoding,
        scaler_type=scaler_type,
        drop_rwma=drop_rwma,
        drop_bmi=drop_bmi,
    )
    model = _prepare_fold_estimator(base_estimator, model_name)

    full_pipeline = Pipeline([
        ("preprocessing", prep_pipe),
        ("classifier", model),
    ])

    if calibration_method and model_name != "Dummy":
        min_class_count = int(np.min(class_counts))
        if min_class_count < 2:
            logger.warning(
                "Insufficient minority class count (%d < 2) for %s calibration; falling back to uncalibrated pipeline.",
                min_class_count,
                calibration_method,
            )
            full_pipeline.fit(X_fit, y_fit)
            return full_pipeline

        cal_splits = min(3, min_class_count)
        cal_cv = StratifiedKFold(n_splits=cal_splits, shuffle=True, random_state=seed)
        calibrated_estimator = CalibratedClassifierCV(
            estimator=full_pipeline,
            method=calibration_method,
            cv=cal_cv,
        )
        calibrated_estimator.fit(X_fit, y_fit)
        return calibrated_estimator

    full_pipeline.fit(X_fit, y_fit)
    return full_pipeline


def _select_threshold_inner_oof(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str,
    base_estimator: Any,
    vhd_encoding: Literal["onehot", "ordinal"],
    scaler_type: Literal["none", "standard", "robust"],
    drop_rwma: bool,
    drop_bmi: bool,
    calibration_method: Optional[Literal["sigmoid", "isotonic"]],
    inner_n_splits: int,
    threshold_metric: str,
    fold_seed: int,
) -> float:
    """
    Selects the classification threshold strictly via stratified inner out-of-fold
    (OOF) predictions within the outer training fold (X_train, y_train).

    Procedure:
    1. Split (X_train, y_train) into stratified inner folds using `fold_seed`.
    2. For each inner fold, fit preprocessing, class weighting, estimator, and
       optional calibration strictly on the inner training partition.
    3. Predict probabilities on the held-out inner validation partition, yielding
       exactly one OOF probability per outer-training observation.
    4. Optimize the decision threshold on (y_train, inner_oof_probs) only.
    5. Fall back safely to 0.5 when class counts are insufficient (< 2 per class).
    """
    y_arr = np.asarray(y_train)
    unique_classes, class_counts = np.unique(y_arr, return_counts=True)

    if len(unique_classes) < 2 or int(np.min(class_counts)) < 2:
        logger.warning(
            "Insufficient class counts (%s) for stratified inner OOF threshold selection; using default 0.5.",
            dict(zip(unique_classes.tolist(), class_counts.tolist(), strict=True)),
        )
        return 0.5

    effective_inner_splits = min(inner_n_splits, int(np.min(class_counts)))
    inner_skf = StratifiedKFold(
        n_splits=effective_inner_splits,
        shuffle=True,
        random_state=fold_seed,
    )

    inner_oof_probs = np.empty(len(X_train), dtype=float)
    filled_mask = np.zeros(len(X_train), dtype=bool)

    for inner_idx, (in_train_idx, in_val_idx) in enumerate(inner_skf.split(X_train, y_train)):
        X_in_train = X_train.iloc[in_train_idx]
        y_in_train = y_train.iloc[in_train_idx]
        X_in_val = X_train.iloc[in_val_idx]

        inner_fitted = _build_and_fit_fold_model(
            X_fit=X_in_train,
            y_fit=y_in_train,
            model_name=model_name,
            base_estimator=base_estimator,
            vhd_encoding=vhd_encoding,
            scaler_type=scaler_type,
            drop_rwma=drop_rwma,
            drop_bmi=drop_bmi,
            calibration_method=calibration_method,
            seed=fold_seed * 100 + inner_idx,
        )
        inner_oof_probs[in_val_idx] = _extract_positive_probs(inner_fitted, X_in_val)
        filled_mask[in_val_idx] = True

    if not filled_mask.all():
        raise RuntimeError("Inner OOF threshold selection failed to generate predictions for all training rows.")

    return find_optimal_threshold(y_arr, inner_oof_probs, metric=threshold_metric)


def evaluate_pipeline_cv(
    X: pd.DataFrame,
    y: pd.Series,
    model_name: str,
    base_estimator: Any,
    vhd_encoding: Literal["onehot", "ordinal"] = "onehot",
    scaler_type: Literal["none", "standard", "robust"] = "none",
    drop_rwma: bool = False,
    drop_bmi: bool = False,
    calibration_method: Optional[Literal["sigmoid", "isotonic"]] = None,
    n_splits: int = 5,
    n_repeats: int = 5,
    random_state: int = 42,
    inner_n_splits: int = 5,
    threshold_metric: str = "f1",
) -> Dict[str, Any]:
    """
    Evaluates an end-to-end Pipeline inside Repeated Stratified K-Fold.

    Leakage-Prevention Guarantees:
    - Preprocessing and classifier are encapsulated in a single sklearn Pipeline.
    - When calibration is enabled, the full Pipeline is passed to
      CalibratedClassifierCV so preprocessing fits independently inside every
      internal calibration training partition.
    - XGBoost `scale_pos_weight` is computed strictly from each training fold's labels.
    - Decision threshold optimization uses stratified inner out-of-fold (OOF)
      predictions generated strictly within each outer training fold.
    - Outer test folds are completely isolated until final fold evaluation.
    """
    if n_splits < 2:
        raise ValueError(f"n_splits must be >= 2, got {n_splits}.")
    if n_repeats < 1:
        raise ValueError(f"n_repeats must be >= 1, got {n_repeats}.")
    if inner_n_splits < 2:
        raise ValueError(f"inner_n_splits must be >= 2, got {inner_n_splits}.")
    if calibration_method is not None and calibration_method not in ("sigmoid", "isotonic"):
        raise ValueError(
            f"Unsupported calibration_method {calibration_method!r}; expected None, 'sigmoid', or 'isotonic'."
        )
    _validate_threshold_metric(threshold_metric)

    rskf = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
    )

    fold_metrics = []
    opt_fold_metrics = []
    selected_thresholds: List[float] = []
    oof_y_true = []
    oof_y_prob = []

    for fold_idx, (train_idx, test_idx) in enumerate(rskf.split(X, y)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        fold_seed = random_state + fold_idx

        # 1. Select optimal threshold strictly via inner OOF predictions on (X_train, y_train)
        if hasattr(base_estimator, "predict_proba"):
            opt_thresh = _select_threshold_inner_oof(
                X_train=X_train,
                y_train=y_train,
                model_name=model_name,
                base_estimator=base_estimator,
                vhd_encoding=vhd_encoding,
                scaler_type=scaler_type,
                drop_rwma=drop_rwma,
                drop_bmi=drop_bmi,
                calibration_method=calibration_method,
                inner_n_splits=inner_n_splits,
                threshold_metric=threshold_metric,
                fold_seed=fold_seed,
            )
        else:
            opt_thresh = 0.5

        # 2. Fit outer-fold Pipeline (or CalibratedClassifierCV wrapping Pipeline) on (X_train, y_train)
        fitted_estimator = _build_and_fit_fold_model(
            X_fit=X_train,
            y_fit=y_train,
            model_name=model_name,
            base_estimator=base_estimator,
            vhd_encoding=vhd_encoding,
            scaler_type=scaler_type,
            drop_rwma=drop_rwma,
            drop_bmi=drop_bmi,
            calibration_method=calibration_method,
            seed=fold_seed,
        )

        # 3. Evaluate on untouched outer test fold
        test_probs = _extract_positive_probs(fitted_estimator, X_test)

        # Standard metrics (thresh = 0.5)
        m_standard = compute_metrics(y_test.values, test_probs, threshold=0.5)
        fold_metrics.append(m_standard)

        # Inner-OOF tuned threshold metrics
        m_tuned = compute_metrics(y_test.values, test_probs, threshold=opt_thresh)
        opt_fold_metrics.append(m_tuned)
        selected_thresholds.append(float(opt_thresh))

        oof_y_true.extend([int(x) for x in y_test.values])
        oof_y_prob.extend([float(x) for x in test_probs])

    summary_standard = aggregate_cv_metrics(fold_metrics)
    summary_tuned = aggregate_cv_metrics(opt_fold_metrics)

    return {
        "model_name": model_name,
        "vhd_encoding": vhd_encoding,
        "scaler_type": scaler_type,
        "drop_rwma": drop_rwma,
        "drop_bmi": drop_bmi,
        "calibration": calibration_method or "uncalibrated",
        "standard_threshold_metrics": summary_standard,
        "tuned_threshold_metrics": summary_tuned,
        "selected_thresholds": selected_thresholds,
        "evaluation_protocol": {
            "validation_type": "internal_repeated_stratified_cv",
            "is_external_validation": False,
            "n_splits": n_splits,
            "n_repeats": n_repeats,
            "total_fold_evaluations": len(fold_metrics),
            "inner_oof_threshold_splits": inner_n_splits,
            "threshold_optimization_metric": threshold_metric,
            "random_state": random_state,
            "note": (
                "Repeated-CV fold summaries reuse the same cohort across repeats; "
                "folds are not independent datasets and do not constitute external validation."
            ),
        },
        "oof_y_true": oof_y_true,
        "oof_y_prob": oof_y_prob,
    }


def run_comprehensive_target_benchmarks(
    df: pd.DataFrame,
    targets_to_evaluate: Optional[List[str]] = None,
    n_splits: int = 5,
    n_repeats: int = 5,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Executes the Stage 2 internal repeated-CV benchmark matrix across all 4 targets:
    - Baseline model comparison (Dummy, Logistic Regression, Random Forest, XGBoost)
    - Preprocessing comparison (One-Hot vs Ordinal; Unscaled vs StandardScaler vs RobustScaler)
    - Ablation study (With vs Without Region RWMA)
    - Collinearity study (With vs Without BMI)
    - Probability Calibration evaluation (Uncalibrated vs Sigmoid vs Isotonic)

    Note: XGBoost `scale_pos_weight` is computed strictly inside each training fold
    by `evaluate_pipeline_cv`, never from the full target vector.
    """
    X, targets = extract_features_and_targets(df)
    target_names = targets_to_evaluate or ["Cath", "LAD", "LCX", "RCA"]
    benchmark_results = {}

    for t_name in target_names:
        y = targets[t_name]
        logger.info(f"=== BENCHMARKING TARGET: {t_name} (Positives: {y.sum()}/{len(y)}) ===")

        # Neutral pos_weight=1.0 placeholder; evaluate_pipeline_cv derives fold-specific
        # scale_pos_weight strictly from each training partition's labels.
        model_instances = get_model_instances(
            pos_weight=1.0, random_state=random_state
        )

        target_records = {
            "baseline_models": {},
            "preprocessing_comparison": {},
            "rwma_ablation": {},
            "bmi_ablation": {},
            "calibration_comparison": {},
        }

        # -------------------------------------------------------------
        # 1. BASELINE MODEL BENCHMARK (One-Hot + StandardScaler)
        # -------------------------------------------------------------
        for m_name, estimator in model_instances.items():
            scaler = "standard" if m_name == "LogisticRegression" else "none"
            res = evaluate_pipeline_cv(
                X, y, m_name, estimator,
                vhd_encoding="onehot",
                scaler_type=scaler,
                drop_rwma=False,
                drop_bmi=False,
                n_splits=n_splits,
                n_repeats=n_repeats,
                random_state=random_state,
            )
            target_records["baseline_models"][m_name] = res

        # -------------------------------------------------------------
        # 2. PREPROCESSING COMPARISONS (Encoding & Scaling)
        # Evaluated on XGBoost across encoding & scaler combinations
        # -------------------------------------------------------------
        for enc in ["onehot", "ordinal"]:
            for scl in ["none", "standard", "robust"]:
                label = f"XGBoost_{enc}_{scl}"
                target_records["preprocessing_comparison"][label] = evaluate_pipeline_cv(
                    X, y, "XGBoost", model_instances["XGBoost"],
                    vhd_encoding=enc,
                    scaler_type=scl,
                    drop_rwma=False,
                    drop_bmi=False,
                    n_splits=n_splits,
                    n_repeats=n_repeats,
                    random_state=random_state,
                )

        # -------------------------------------------------------------
        # 3. CONTROLLED ABLATION STUDY: REGION RWMA
        # With vs Without Region RWMA across all candidate models
        # -------------------------------------------------------------
        for m_name in ["LogisticRegression", "RandomForest", "XGBoost"]:
            scaler = "standard" if m_name == "LogisticRegression" else "none"
            res_with = evaluate_pipeline_cv(
                X, y, m_name, model_instances[m_name],
                vhd_encoding="onehot", scaler_type=scaler, drop_rwma=False,
                n_splits=n_splits, n_repeats=n_repeats, random_state=random_state,
            )
            res_without = evaluate_pipeline_cv(
                X, y, m_name, model_instances[m_name],
                vhd_encoding="onehot", scaler_type=scaler, drop_rwma=True,
                n_splits=n_splits, n_repeats=n_repeats, random_state=random_state,
            )
            target_records["rwma_ablation"][m_name] = {
                "with_rwma": res_with,
                "without_rwma": res_without,
            }

        # -------------------------------------------------------------
        # 4. COLLINEARITY ABLATION STUDY: BMI
        # With vs Without BMI across all models
        # -------------------------------------------------------------
        for m_name in ["LogisticRegression", "RandomForest", "XGBoost"]:
            scaler = "standard" if m_name == "LogisticRegression" else "none"
            res_with_bmi = evaluate_pipeline_cv(
                X, y, m_name, model_instances[m_name],
                vhd_encoding="onehot", scaler_type=scaler, drop_bmi=False,
                n_splits=n_splits, n_repeats=n_repeats, random_state=random_state,
            )
            res_without_bmi = evaluate_pipeline_cv(
                X, y, m_name, model_instances[m_name],
                vhd_encoding="onehot", scaler_type=scaler, drop_bmi=True,
                n_splits=n_splits, n_repeats=n_repeats, random_state=random_state,
            )
            target_records["bmi_ablation"][m_name] = {
                "with_bmi": res_with_bmi,
                "without_bmi": res_without_bmi,
            }

        # -------------------------------------------------------------
        # 5. PROBABILITY CALIBRATION BENCHMARK
        # Uncalibrated vs Sigmoid (Platt) vs Isotonic
        # -------------------------------------------------------------
        for cal_method in [None, "sigmoid", "isotonic"]:
            cal_label = cal_method or "uncalibrated"
            for m_name in ["LogisticRegression", "XGBoost"]:
                scaler = "standard" if m_name == "LogisticRegression" else "none"
                res_cal = evaluate_pipeline_cv(
                    X, y, m_name, model_instances[m_name],
                    vhd_encoding="onehot", scaler_type=scaler,
                    calibration_method=cal_method,
                    n_splits=n_splits, n_repeats=n_repeats, random_state=random_state,
                )
                target_records["calibration_comparison"][f"{m_name}_{cal_label}"] = res_cal

        benchmark_results[t_name] = target_records

    return benchmark_results
