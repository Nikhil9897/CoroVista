"""
CoroVista - Model Benchmarking & Validation Engine
Stage 2: Machine Learning Foundation

Conducts rigorous, leakage-safe Repeated Stratified K-Fold Cross-Validation:
- 5 Folds x 5 Repeats = 25 evaluation runs per model/target configuration.
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
- Evaluates Probability Calibration:
  - Uncalibrated vs Sigmoid (Platt) vs Isotonic
- Performs Out-of-Fold Threshold Optimization.
"""

import copy
import logging
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from xgboost import XGBClassifier

from ml.evaluation.metrics import aggregate_cv_metrics, compute_metrics, find_optimal_threshold
from ml.preprocessing.pipeline import build_preprocessing_pipeline, extract_features_and_targets

logger = logging.getLogger("corovista_benchmark")


def get_model_instances(
    pos_weight: float = 1.0,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Instantiates the baseline model candidates with reproducible seeds."""
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
        "XGBoost": XGBClassifier(
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
) -> Dict[str, Any]:
    """
    Evaluates an end-to-end Pipeline inside Repeated Stratified K-Fold.
    Ensures that NO preprocessing information leaks between folds.
    """
    rskf = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
    )

    fold_metrics = []
    opt_fold_metrics = []
    oof_y_true = []
    oof_y_prob = []
    oof_y_prob_uncal = []

    for fold_idx, (train_idx, test_idx) in enumerate(rskf.split(X, y)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        # 1. Build fresh preprocessing pipeline for this fold
        prep_pipe = build_preprocessing_pipeline(
            vhd_encoding=vhd_encoding,
            scaler_type=scaler_type,
            drop_rwma=drop_rwma,
            drop_bmi=drop_bmi,
        )

        # 2. Fit preprocessing strictly on training fold
        X_train_trans = prep_pipe.fit_transform(X_train)
        X_test_trans = prep_pipe.transform(X_test)

        # 3. Model instantiation and training
        model = copy.deepcopy(base_estimator)

        if calibration_method and model_name != "Dummy":
            # Calibrate model using internal cross-validation on train fold
            fitted_estimator = CalibratedClassifierCV(
                estimator=model,
                method=calibration_method,
                cv=3,
            )
            fitted_estimator.fit(X_train_trans, y_train)
        else:
            model.fit(X_train_trans, y_train)
            fitted_estimator = model

        if hasattr(fitted_estimator, "predict_proba"):
            test_probs = fitted_estimator.predict_proba(X_test_trans)[:, 1]
            train_probs = fitted_estimator.predict_proba(X_train_trans)[:, 1]
        else:
            test_probs = fitted_estimator.predict(X_test_trans).astype(float)
            train_probs = None

        opt_thresh = find_optimal_threshold(y_train.values, train_probs) if train_probs is not None else 0.5

        # Standard metrics (thresh = 0.5)
        m_standard = compute_metrics(y_test.values, test_probs, threshold=0.5)
        fold_metrics.append(m_standard)

        # Tuned threshold metrics
        m_tuned = compute_metrics(y_test.values, test_probs, threshold=opt_thresh)
        opt_fold_metrics.append(m_tuned)

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
    Executes the full Stage 2 benchmark matrix across all 4 targets:
    - Baseline model comparison (Dummy, Logistic Regression, Random Forest, XGBoost)
    - Preprocessing comparison (One-Hot vs Ordinal; Unscaled vs StandardScaler vs RobustScaler)
    - Ablation study (With vs Without Region RWMA)
    - Collinearity study (With vs Without BMI)
    - Probability Calibration evaluation (Uncalibrated vs Sigmoid vs Isotonic)
    """
    X, targets = extract_features_and_targets(df)
    target_names = targets_to_evaluate or ["Cath", "LAD", "LCX", "RCA"]
    benchmark_results = {}

    for t_name in target_names:
        y = targets[t_name]
        logger.info(f"=== BENCHMARKING TARGET: {t_name} (Positives: {y.sum()}/{len(y)}) ===")

        # Compute target-specific imbalance ratio for XGBoost
        n_pos = int(y.sum())
        n_neg = len(y) - n_pos
        scale_pos_weight = round(n_neg / n_pos, 3) if n_pos > 0 else 1.0

        model_instances = get_model_instances(
            pos_weight=scale_pos_weight, random_state=random_state
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
        # Evaluated on top linear (LogisticRegression) & tree (XGBoost)
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
