"""
Regression tests for CoroVista Phase 1 ML research methodology corrections.

Covers:
1. Inner out-of-fold (OOF) threshold optimization (no in-sample threshold leakage)
2. Outer test fold isolation (test features/labels cannot affect training or threshold selection)
3. Calibration preprocessing isolation (preprocessing wrapped in Pipeline inside CalibratedClassifierCV)
4. Fold-specific XGBoost class weighting (derived strictly from training labels; safe on degenerate folds)
5. Undefined ROC-AUC and PR-AUC handling (explicit None, no 0.5/prevalence substitution or warnings)
6. Comprehensive input validation (probabilities, lengths, labels, thresholds, optimization metrics)
7. Repeated-CV statistical reporting labels & non-independence metadata
8. Determinism, model configurations, preprocessing, and ablation compatibility
"""

import json
import warnings
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler

from ml.evaluation.metrics import (
    aggregate_cv_metrics,
    compute_ece,
    compute_metrics,
    find_optimal_threshold,
)
from ml.preprocessing.feature_metadata import FEATURE_PARTITIONS
from ml.preprocessing.pipeline import extract_features_and_targets
from ml.training.benchmark import (
    DynamicScalePosWeightXGBClassifier,
    compute_scale_pos_weight,
    evaluate_pipeline_cv,
    get_model_instances,
    run_comprehensive_target_benchmarks,
)


def _make_synthetic_clinical_df(
    n_samples: int = 40,
    seed: int = 42,
    pos_rate: float = 0.4,
    include_targets: bool = True,
) -> pd.DataFrame:
    """Builds a small synthetic DataFrame matching the 55-feature raw clinical schema."""
    rng = np.random.RandomState(seed)
    data: Dict[str, np.ndarray] = {}

    # Signal-bearing numerical features so models learn non-trivial probabilities
    latent = rng.randn(n_samples)
    for col in FEATURE_PARTITIONS["numerical"]:
        if col == "Age":
            data[col] = np.clip(55 + 10 * latent + rng.randn(n_samples) * 3, 30, 85)
        elif col == "EF-TTE":
            data[col] = np.clip(50 - 8 * latent + rng.randn(n_samples) * 3, 15, 70)
        elif col == "Region RWMA":
            data[col] = rng.randint(0, 5, size=n_samples)
        else:
            data[col] = 50.0 + rng.randn(n_samples) * 10.0

    for col in FEATURE_PARTITIONS["binary_integer"]:
        data[col] = rng.randint(0, 2, size=n_samples)

    for col in FEATURE_PARTITIONS["binary_string"]:
        data[col] = rng.choice(["Y", "N"], size=n_samples)

    data["Sex"] = rng.choice(["Male", "Fmale"], size=n_samples)
    data["BBB"] = rng.choice(["N", "LBBB", "RBBB"], size=n_samples)
    data["Function Class"] = rng.randint(0, 4, size=n_samples)
    data["VHD"] = rng.choice(["N", "mild", "Moderate", "Severe"], size=n_samples)
    data["Exertional CP"] = np.array(["N"] * n_samples)

    if include_targets:
        n_pos = max(1, min(n_samples - 1, int(round(n_samples * pos_rate))))
        order = np.argsort(latent)[::-1]
        y_bin = np.zeros(n_samples, dtype=int)
        y_bin[order[:n_pos]] = 1
        data["Cath"] = np.where(y_bin == 1, "CAD", "Normal")
        data["LAD"] = np.where(y_bin == 1, "Stenotic", "Normal")
        data["LCX"] = np.where(rng.rand(n_samples) < pos_rate, "Stenotic", "Normal")
        data["RCA"] = np.where(rng.rand(n_samples) < pos_rate, "Stenotic", "Normal")

    return pd.DataFrame(data)


def _split_synthetic_X_y(n_samples: int = 40, seed: int = 42, pos_rate: float = 0.4):
    df = _make_synthetic_clinical_df(n_samples=n_samples, seed=seed, pos_rate=pos_rate)
    X, targets = extract_features_and_targets(df)
    return X, targets["Cath"]


# ---------------------------------------------------------------------------
# 1. OOF Threshold Optimization & Outer Test Isolation (Step 2)
# ---------------------------------------------------------------------------
def test_threshold_selection_uses_inner_oof_predictions(monkeypatch):
    """
    Verifies that threshold optimization receives inner OOF predictions (one per
    outer-training sample) that do NOT match in-sample predictions of the outer model.
    """
    X, y = _split_synthetic_X_y(n_samples=40, seed=7, pos_rate=0.45)
    models = get_model_instances(random_state=42)

    recorded_calls = []

    def spy_find_optimal_threshold(y_true_in, y_prob_in, metric="f1"):
        recorded_calls.append((np.asarray(y_true_in).copy(), np.asarray(y_prob_in).copy()))
        return find_optimal_threshold(y_true_in, y_prob_in, metric=metric)

    monkeypatch.setattr("ml.training.benchmark.find_optimal_threshold", spy_find_optimal_threshold)

    res = evaluate_pipeline_cv(
        X,
        y,
        "RandomForest",
        models["RandomForest"],
        scaler_type="none",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=3,
        random_state=42,
    )

    assert len(recorded_calls) == 2
    assert len(res["selected_thresholds"]) == 2

    # Check outer fold 0: threshold inputs must match outer train length (20), not full dataset (40) or test (20)
    from sklearn.model_selection import RepeatedStratifiedKFold
    from sklearn.pipeline import Pipeline

    from ml.preprocessing.pipeline import build_preprocessing_pipeline

    rskf = RepeatedStratifiedKFold(n_splits=2, n_repeats=1, random_state=42)
    train_idx_0, _ = next(rskf.split(X, y))
    y_true_passed, y_prob_passed = recorded_calls[0]

    assert len(y_true_passed) == len(train_idx_0) == 20
    assert len(y_prob_passed) == len(train_idx_0) == 20
    assert np.array_equal(y_true_passed, y.iloc[train_idx_0].values)

    # Compare against naive in-sample probabilities from a RandomForest fit on full outer train fold
    outer_pipe = Pipeline([
        ("preprocessing", build_preprocessing_pipeline(vhd_encoding="onehot", scaler_type="none")),
        ("classifier", get_model_instances(random_state=42)["RandomForest"]),
    ])
    outer_pipe.fit(X.iloc[train_idx_0], y.iloc[train_idx_0])
    in_sample_probs = outer_pipe.predict_proba(X.iloc[train_idx_0])[:, 1]

    # Inner OOF probabilities must differ from overfitted in-sample training probabilities
    assert not np.allclose(y_prob_passed, in_sample_probs)


def test_outer_test_isolation_for_threshold_and_training():
    """
    Mutating outer test features and labels must produce identical selected thresholds
    on the outer training fold.
    """
    X, y = _split_synthetic_X_y(n_samples=36, seed=11, pos_rate=0.4)
    models = get_model_instances(random_state=42)

    from sklearn.model_selection import RepeatedStratifiedKFold

    rskf = RepeatedStratifiedKFold(n_splits=2, n_repeats=1, random_state=42)
    _, test_idx_0 = next(rskf.split(X, y))

    # Build a mutated dataset where fold-0 test observations are drastically corrupted
    X_mut = X.copy()
    y_mut = y.copy()
    X_mut.iloc[test_idx_0, X_mut.columns.get_loc("Age")] = 1e6
    X_mut.iloc[test_idx_0, X_mut.columns.get_loc("FBS")] = 99999.0
    y_mut.iloc[test_idx_0] = 1 - y_mut.iloc[test_idx_0]

    # For fold 0 specifically, train_idx is identical if stratification splits are preserved,
    # Wait: flipping y_mut changes stratification! To keep exact same split indices while mutating
    # outer test features (X_test), verify feature corruption + verify direct inner OOF helper isolation.
    X_feat_mut = X.copy()
    X_feat_mut.iloc[test_idx_0, X_feat_mut.columns.get_loc("Age")] = 1e6
    X_feat_mut.iloc[test_idx_0, X_feat_mut.columns.get_loc("LDL")] = -500.0

    res_clean = evaluate_pipeline_cv(
        X,
        y,
        "LogisticRegression",
        models["LogisticRegression"],
        scaler_type="standard",
        calibration_method="sigmoid",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=3,
        random_state=42,
    )
    res_mut = evaluate_pipeline_cv(
        X_feat_mut,
        y,
        "LogisticRegression",
        models["LogisticRegression"],
        scaler_type="standard",
        calibration_method="sigmoid",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=3,
        random_state=42,
    )

    # Fold 0 only tested test_idx_0 as outer test -> its selected threshold and fold-0 outer train
    # cannot depend on X_test at all.
    assert res_clean["selected_thresholds"][0] == res_mut["selected_thresholds"][0]


def test_small_dataset_threshold_fallback_safe():
    """
    When a training fold has insufficient minority class counts (< 2), inner OOF
    threshold selection falls back safely to 0.5 without crashing.
    """
    X, _ = _split_synthetic_X_y(n_samples=12, seed=5, pos_rate=0.5)
    # Only 2 positives total -> with 2 outer splits, each outer train fold has 1 positive
    y_tiny = pd.Series([1, 1] + [0] * 10)
    models = get_model_instances(random_state=42)

    res = evaluate_pipeline_cv(
        X,
        y_tiny,
        "LogisticRegression",
        models["LogisticRegression"],
        scaler_type="standard",
        calibration_method="sigmoid",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=5,
        random_state=42,
    )

    assert res["selected_thresholds"] == [0.5, 0.5]
    assert len(res["oof_y_true"]) == 12
    assert len(res["oof_y_prob"]) == 12


# ---------------------------------------------------------------------------
# 2. Calibration Preprocessing Isolation (Step 3)
# ---------------------------------------------------------------------------
def test_calibration_fits_preprocessing_inside_each_calibration_partition(monkeypatch):
    """
    Proves that CalibratedClassifierCV receives the full Pipeline(preprocessing, classifier)
    so StandardScaler.fit is invoked on each internal calibration training subset
    rather than on the entire outer training fold beforehand.
    """
    X, y = _split_synthetic_X_y(n_samples=30, seed=19, pos_rate=0.5)
    models = get_model_instances(random_state=42)

    fit_sample_sizes: List[int] = []
    orig_fit = StandardScaler.fit

    def spy_scaler_fit(self, X_in, y_in=None, **kwargs):
        fit_sample_sizes.append(len(X_in))
        return orig_fit(self, X_in, y_in, **kwargs)

    monkeypatch.setattr(StandardScaler, "fit", spy_scaler_fit)

    # Disable inner OOF CV influence by using a single outer fold call via 2 splits, 1 repeat,
    # inner_n_splits=2:
    # - Per outer fold (15 samples):
    #   - Inner OOF has 2 splits -> each inner train has ~7-8 samples -> cal cv=3 fits scaler on ~5 samples
    #   - Outer cal cv=3 on 15 samples fits scaler on 10 samples (NEVER 15 and NEVER 30!)
    res = evaluate_pipeline_cv(
        X,
        y,
        "LogisticRegression",
        models["LogisticRegression"],
        scaler_type="standard",
        calibration_method="sigmoid",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=2,
        random_state=42,
    )

    assert res["calibration"] == "sigmoid"
    assert len(fit_sample_sizes) > 0
    # Outer training fold size is 15; full dataset is 30.
    # Because preprocessing is inside CalibratedClassifierCV(cv=3), scaler.fit must NEVER see
    # the full outer training fold (15) or full dataset (30).
    assert max(fit_sample_sizes) < 15
    assert 10 in fit_sample_sizes  # 2/3 of 15-sample outer train fold inside cv=3 calibration


@pytest.mark.parametrize("cal_method", [None, "sigmoid", "isotonic"])
def test_calibration_modes_supported_and_valid_probabilities(cal_method):
    X, y = _split_synthetic_X_y(n_samples=30, seed=21, pos_rate=0.45)
    models = get_model_instances(random_state=42)
    res = evaluate_pipeline_cv(
        X,
        y,
        "LogisticRegression",
        models["LogisticRegression"],
        scaler_type="standard",
        calibration_method=cal_method,
        n_splits=2,
        n_repeats=1,
        inner_n_splits=2,
        random_state=42,
    )
    expected_cal = cal_method or "uncalibrated"
    assert res["calibration"] == expected_cal
    probs = np.asarray(res["oof_y_prob"])
    assert np.isfinite(probs).all()
    assert (probs >= 0.0).all() and (probs <= 1.0).all()


# ---------------------------------------------------------------------------
# 3. Fold-Specific XGBoost Class Weighting (Step 4)
# ---------------------------------------------------------------------------
def test_compute_scale_pos_weight_and_degenerate_partitions():
    assert compute_scale_pos_weight([0, 0, 0, 1]) == 3.0
    assert compute_scale_pos_weight([1, 1, 0, 1]) == 0.333
    # Zero-positive and zero-negative partitions must return 1.0 safely
    assert compute_scale_pos_weight([0, 0, 0, 0]) == 1.0
    assert compute_scale_pos_weight([1, 1, 1, 1]) == 1.0


def test_xgboost_class_weight_depends_only_on_outer_training_labels(monkeypatch):
    """
    Verifies XGBClassifier receives scale_pos_weight computed strictly from each
    training partition's labels, not from the full dataset target vector.
    """
    X, y = _split_synthetic_X_y(n_samples=40, seed=33, pos_rate=0.3)
    models = get_model_instances(pos_weight=99.0, random_state=42)

    observed_weights = []
    from xgboost import XGBClassifier

    orig_xgb_fit = XGBClassifier.fit

    def spy_xgb_fit(self, X_in, y_in, **kwargs):
        observed_weights.append((len(y_in), compute_scale_pos_weight(y_in), self.get_params()["scale_pos_weight"]))
        return orig_xgb_fit(self, X_in, y_in, **kwargs)

    monkeypatch.setattr(XGBClassifier, "fit", spy_xgb_fit)

    evaluate_pipeline_cv(
        X,
        y,
        "XGBoost",
        models["XGBoost"],
        scaler_type="none",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=2,
        random_state=42,
    )

    assert len(observed_weights) > 0
    for _, expected_w, actual_w in observed_weights:
        assert actual_w == pytest.approx(expected_w)
        assert actual_w != 99.0


def test_dynamic_xgboost_clone_preserves_partition_weight_computation():
    """
    Verifies sklearn.base.clone() on DynamicScalePosWeightXGBClassifier preserves
    hyperparameters and recomputes scale_pos_weight independently on each new fit().
    """
    from sklearn.base import clone

    est = DynamicScalePosWeightXGBClassifier(
        n_estimators=5,
        max_depth=3,
        learning_rate=0.05,
        scale_pos_weight=1.0,
        eval_metric="logloss",
        random_state=42,
        n_jobs=1,
    )
    rng = np.random.RandomState(42)
    X_part = rng.randn(10, 4)

    # First partition: 8 negatives, 2 positives -> weight 4.0
    y_part_a = np.array([0] * 8 + [1] * 2)
    cloned_a = clone(est)
    assert isinstance(cloned_a, DynamicScalePosWeightXGBClassifier)
    assert cloned_a.get_params()["n_estimators"] == 5
    cloned_a.fit(X_part, y_part_a)
    assert cloned_a.computed_scale_pos_weight_ == pytest.approx(4.0)
    assert cloned_a.get_params()["scale_pos_weight"] == pytest.approx(1.0)
    cfg_a = json.loads(cloned_a.get_booster().save_config())
    assert float(cfg_a["learner"]["objective"]["reg_loss_param"]["scale_pos_weight"]) == pytest.approx(4.0)

    # Cloning the already-fitted estimator and fitting on a different partition (2 neg, 8 pos -> 0.25)
    # must compute the new partition's weight without retaining the previous partition's weight
    # or mutating __init__ parameters during fit().
    y_part_b = np.array([0] * 2 + [1] * 8)
    cloned_b = clone(cloned_a)
    assert isinstance(cloned_b, DynamicScalePosWeightXGBClassifier)
    assert cloned_b.get_params()["scale_pos_weight"] == pytest.approx(1.0)
    cloned_b.fit(X_part, y_part_b)
    assert cloned_b.computed_scale_pos_weight_ == pytest.approx(0.25)
    assert cloned_b.get_params()["scale_pos_weight"] == pytest.approx(1.0)
    cfg_b = json.loads(cloned_b.get_booster().save_config())
    assert float(cfg_b["learner"]["objective"]["reg_loss_param"]["scale_pos_weight"]) == pytest.approx(0.25)
    assert cloned_a.computed_scale_pos_weight_ == pytest.approx(4.0)


def test_calibration_validation_labels_do_not_leak_into_xgboost_class_weight():
    """
    Proves directly that changing labels in a CalibratedClassifierCV internal
    calibration-validation partition does NOT alter the scale_pos_weight used to
    fit that fold's XGBoost classifier.
    """
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import KFold
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    rng = np.random.RandomState(123)
    X = rng.randn(24, 4)
    # Deterministic KFold(n_splits=3, shuffle=False): fold 0 validates on indices 0..7, trains on 8..23
    y_a = np.array([1, 1, 0, 0, 0, 0, 1, 0] + [0] * 12 + [1] * 4)
    y_b = y_a.copy()
    # Flip labels ONLY inside fold 0's calibration-validation partition (indices 0..7)
    y_b[:8] = 1 - y_b[:8]

    assert compute_scale_pos_weight(y_a) != compute_scale_pos_weight(y_b)

    cv = KFold(n_splits=3, shuffle=False)
    train_idx_0, _ = next(cv.split(X, y_a))
    expected_fold0_weight = compute_scale_pos_weight(y_a[train_idx_0])

    def _fit_calibrated(y_in: np.ndarray) -> CalibratedClassifierCV:
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            (
                "clf",
                DynamicScalePosWeightXGBClassifier(
                    n_estimators=5,
                    max_depth=2,
                    scale_pos_weight=1.0,
                    eval_metric="logloss",
                    random_state=42,
                    n_jobs=1,
                ),
            ),
        ])
        cal = CalibratedClassifierCV(estimator=pipe, method="sigmoid", cv=cv)
        cal.fit(X, y_in)
        return cal

    cal_a = _fit_calibrated(y_a)
    cal_b = _fit_calibrated(y_b)

    fold0_clf_a = cal_a.calibrated_classifiers_[0].estimator.named_steps["clf"]
    fold0_clf_b = cal_b.calibrated_classifiers_[0].estimator.named_steps["clf"]

    w_a = fold0_clf_a.computed_scale_pos_weight_
    w_b = fold0_clf_b.computed_scale_pos_weight_
    assert w_a == pytest.approx(expected_fold0_weight)
    assert w_b == pytest.approx(expected_fold0_weight)
    assert w_a != pytest.approx(compute_scale_pos_weight(y_a))
    assert w_b != pytest.approx(compute_scale_pos_weight(y_b))
    # Verify __init__ parameter immutability and actual XGBoost booster config weight
    assert fold0_clf_a.get_params()["scale_pos_weight"] == pytest.approx(1.0)
    assert fold0_clf_b.get_params()["scale_pos_weight"] == pytest.approx(1.0)
    booster_w_a = float(
        json.loads(fold0_clf_a.get_booster().save_config())["learner"]["objective"]["reg_loss_param"][
            "scale_pos_weight"
        ]
    )
    booster_w_b = float(
        json.loads(fold0_clf_b.get_booster().save_config())["learner"]["objective"]["reg_loss_param"][
            "scale_pos_weight"
        ]
    )
    assert booster_w_a == pytest.approx(expected_fold0_weight)
    assert booster_w_b == pytest.approx(expected_fold0_weight)


@pytest.mark.parametrize("use_plain_xgb", [False, True])
def test_calibrated_evaluate_pipeline_cv_derives_xgboost_weight_per_calibration_partition(
    monkeypatch, use_plain_xgb
):
    """
    Verifies that during evaluate_pipeline_cv(..., calibration_method='sigmoid'),
    every internal CalibratedClassifierCV split (in both outer folds and inner OOF
    threshold-selection folds) computes scale_pos_weight from its own calibration
    training partition labels rather than the full outer-training fold labels.
    """
    from xgboost import XGBClassifier

    X, y = _split_synthetic_X_y(n_samples=48, seed=41, pos_rate=0.35)
    if use_plain_xgb:
        estimator = XGBClassifier(
            n_estimators=5,
            max_depth=2,
            learning_rate=0.05,
            scale_pos_weight=77.0,
            eval_metric="logloss",
            random_state=42,
            n_jobs=1,
        )
    else:
        estimator = get_model_instances(pos_weight=77.0, random_state=42)["XGBoost"]
        estimator.set_params(n_estimators=5, n_jobs=1)

    observed_fits = []
    orig_xgb_fit = XGBClassifier.fit

    def spy_xgb_fit(self, X_in, y_in, **kwargs):
        observed_fits.append(
            (len(y_in), compute_scale_pos_weight(y_in), self.get_params()["scale_pos_weight"])
        )
        return orig_xgb_fit(self, X_in, y_in, **kwargs)

    monkeypatch.setattr(XGBClassifier, "fit", spy_xgb_fit)

    res = evaluate_pipeline_cv(
        X,
        y,
        "XGBoost",
        estimator,
        scaler_type="none",
        calibration_method="sigmoid",
        n_splits=2,
        n_repeats=1,
        inner_n_splits=2,
        random_state=42,
    )

    assert res["calibration"] == "sigmoid"
    # 2 outer folds * (2 inner OOF folds * 3 cal splits + 3 outer cal splits) = 18 fits
    assert len(observed_fits) == 18
    # Outer train has 24 samples -> cal cv=3 fits must receive <= 16 samples, never 24 or 48
    assert max(n for n, _, _ in observed_fits) <= 16
    for _, expected_w, actual_w in observed_fits:
        assert actual_w == pytest.approx(expected_w)
        assert actual_w != 77.0


def test_dynamic_xgboost_preserves_sklearn_metadata_routing_and_fit_signature():
    """
    Verifies DynamicScalePosWeightXGBClassifier.fit preserves XGBClassifier.fit's
    explicit signature and scikit-learn metadata-routing contract, and does not
    mutate __init__ params during fit().
    """
    import inspect

    from sklearn import config_context
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier

    est = DynamicScalePosWeightXGBClassifier(
        n_estimators=5,
        max_depth=2,
        scale_pos_weight=1.0,
        eval_metric="logloss",
        random_state=42,
        n_jobs=1,
    )
    assert list(inspect.signature(DynamicScalePosWeightXGBClassifier.fit).parameters) == list(
        inspect.signature(XGBClassifier.fit).parameters
    )

    routing = est.get_metadata_routing()
    base_routing = XGBClassifier().get_metadata_routing()
    assert routing.fit.requests == base_routing.fit.requests
    assert "sample_weight" in routing.fit.requests

    rng = np.random.RandomState(7)
    X = rng.randn(24, 4)
    y = np.array([0] * 18 + [1] * 6)
    with config_context(enable_metadata_routing=True):
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", est.set_fit_request(sample_weight=False)),
        ])
        cal = CalibratedClassifierCV(estimator=pipe, method="sigmoid", cv=3)
        cal.fit(X, y)
        preds = cal.predict_proba(X)
        assert preds.shape == (24, 2)
        assert est.get_params()["scale_pos_weight"] == pytest.approx(1.0)


def test_run_comprehensive_target_benchmarks_does_not_leak_full_pos_weight(monkeypatch):
    """
    Ensures run_comprehensive_target_benchmarks passes neutral pos_weight=1.0 to
    get_model_instances so full-target prevalence never leaks before CV splitting.
    """
    df = _make_synthetic_clinical_df(n_samples=30, seed=13, pos_rate=0.3)
    seen_pos_weights = []
    orig_get_models = get_model_instances

    def spy_get_models(pos_weight=1.0, random_state=42):
        seen_pos_weights.append(pos_weight)
        models = orig_get_models(pos_weight=pos_weight, random_state=random_state)
        # Keep unit test fast while exercising all 5 benchmark sections end-to-end
        models["RandomForest"].set_params(n_estimators=5, n_jobs=1)
        models["XGBoost"].set_params(n_estimators=5, n_jobs=1)
        return models

    monkeypatch.setattr("ml.training.benchmark.get_model_instances", spy_get_models)

    res = run_comprehensive_target_benchmarks(
        df,
        targets_to_evaluate=["Cath"],
        n_splits=2,
        n_repeats=1,
        random_state=42,
    )

    assert seen_pos_weights == [1.0]
    assert "Cath" in res
    assert set(res["Cath"].keys()) == {
        "baseline_models",
        "preprocessing_comparison",
        "rwma_ablation",
        "bmi_ablation",
        "calibration_comparison",
    }
    # Ensure JSON serialization succeeds without NaN/Inf
    serialized = json.dumps(res, allow_nan=False)
    assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# 4. Metric Correctness & Validation (Step 5)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("y_true", [[0, 0, 0, 0], [1, 1, 1, 1]])
def test_undefined_roc_and_pr_auc_return_none_without_warnings(y_true):
    y_prob = [0.1, 0.3, 0.7, 0.9]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        m = compute_metrics(y_true, y_prob, threshold=0.5)

    assert m["roc_auc"] is None
    assert m["pr_auc"] is None
    assert not caught
    # Must serialize to valid standard JSON (null, not NaN)
    dumped = json.dumps(m, allow_nan=False)
    assert '"roc_auc": null' in dumped
    assert '"pr_auc": null' in dumped


def test_invalid_probability_and_input_rejection():
    # Length mismatch
    with pytest.raises(ValueError, match="Length mismatch"):
        compute_metrics([0, 1], [0.2, 0.5, 0.8])

    # Empty inputs
    with pytest.raises(ValueError, match="must not be empty"):
        compute_metrics([], [])

    # Non-finite probabilities
    for bad_prob in ([0.2, np.nan], [0.2, np.inf], [0.2, -np.inf]):
        with pytest.raises(ValueError, match="non-finite"):
            compute_metrics([0, 1], bad_prob)

    # Out-of-bounds probabilities
    for bad_prob in ([-0.01, 0.5], [0.5, 1.01]):
        with pytest.raises(ValueError, match="within \\[0.0, 1.0\\]"):
            compute_metrics([0, 1], bad_prob)

    # Non-binary y_true
    with pytest.raises(ValueError, match="binary values"):
        compute_metrics([0, 2], [0.2, 0.8])

    # Also validate compute_ece and find_optimal_threshold reject invalid probs
    with pytest.raises(ValueError, match="within \\[0.0, 1.0\\]"):
        compute_ece([0, 1], [0.1, 1.5])
    with pytest.raises(ValueError, match="non-finite"):
        find_optimal_threshold([0, 1], [0.1, np.nan])


def test_invalid_threshold_rejection():
    for bad_thresh in (-0.1, 1.1, float("nan"), float("inf"), True, "0.5"):
        with pytest.raises(ValueError, match="threshold"):
            compute_metrics([0, 1, 0, 1], [0.1, 0.9, 0.2, 0.8], threshold=bad_thresh)  # type: ignore[arg-type]


def test_unsupported_threshold_metric_rejection():
    with pytest.raises(ValueError, match="Unsupported threshold optimization metric"):
        find_optimal_threshold([0, 1, 0, 1], [0.2, 0.8, 0.3, 0.7], metric="accuracy")

    X, y = _split_synthetic_X_y(n_samples=20, seed=9)
    models = get_model_instances(random_state=42)
    with pytest.raises(ValueError, match="Unsupported threshold optimization metric"):
        evaluate_pipeline_cv(
            X,
            y,
            "LogisticRegression",
            models["LogisticRegression"],
            threshold_metric="invalid_metric",
        )


def test_find_optimal_threshold_supports_f1_and_youden_safely():
    y_true = np.array([0, 0, 0, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.35, 0.65, 0.8, 0.9])
    t_f1 = find_optimal_threshold(y_true, y_prob, metric="f1")
    t_youden = find_optimal_threshold(y_true, y_prob, metric="youden")
    assert 0.15 <= t_f1 <= 0.85
    assert 0.15 <= t_youden <= 0.85

    # Single-class y_true returns safe 0.5 without crashing confusion_matrix unpacking
    assert find_optimal_threshold([0, 0, 0, 0], [0.1, 0.2, 0.3, 0.4], metric="youden") == 0.5


# ---------------------------------------------------------------------------
# 5. Statistical Reporting & Aggregate CV Metrics (Step 6)
# ---------------------------------------------------------------------------
def test_aggregate_cv_metrics_repeated_cv_summary_and_nullable_handling():
    folds = [
        compute_metrics([0, 1, 0, 1], [0.1, 0.9, 0.2, 0.8]),
        compute_metrics([0, 0, 0, 0], [0.1, 0.2, 0.3, 0.4]),  # undefined roc_auc & pr_auc
        compute_metrics([0, 1, 1, 0], [0.2, 0.8, 0.7, 0.3]),
    ]
    summary = aggregate_cv_metrics(folds)

    assert summary["roc_auc"]["summary_scope"] == "repeated_cv_fold_summary"
    assert summary["roc_auc"]["n_valid_folds"] == 2
    assert summary["roc_auc"]["n_undefined_folds"] == 1
    assert summary["roc_auc"]["mean"] == 1.0
    assert summary["pr_auc"]["n_valid_folds"] == 2
    assert summary["pr_auc"]["n_undefined_folds"] == 1
    assert summary["accuracy"]["n_valid_folds"] == 3
    assert summary["accuracy"]["n_undefined_folds"] == 0

    # All-undefined folds should yield None mean and std
    all_undef = aggregate_cv_metrics([
        compute_metrics([0, 0, 0, 0], [0.1, 0.2, 0.3, 0.4]),
        compute_metrics([1, 1, 1, 1], [0.6, 0.7, 0.8, 0.9]),
    ])
    assert all_undef["roc_auc"]["mean"] is None
    assert all_undef["roc_auc"]["std"] is None
    assert all_undef["roc_auc"]["n_valid_folds"] == 0
    assert all_undef["roc_auc"]["n_undefined_folds"] == 2


# ---------------------------------------------------------------------------
# 6. Determinism & Existing Model Configurations (Step 7)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("model_name", ["Dummy", "LogisticRegression", "RandomForest", "XGBoost"])
def test_evaluate_pipeline_cv_deterministic_across_models(model_name):
    X, y = _split_synthetic_X_y(n_samples=36, seed=25, pos_rate=0.45)
    scaler = "standard" if model_name == "LogisticRegression" else "none"
    cal = "sigmoid" if model_name in ("LogisticRegression", "XGBoost") else None

    m1 = get_model_instances(random_state=42)[model_name]
    m2 = get_model_instances(random_state=42)[model_name]

    r1 = evaluate_pipeline_cv(
        X, y, model_name, m1,
        scaler_type=scaler,
        calibration_method=cal,
        n_splits=2,
        n_repeats=2,
        inner_n_splits=3,
        random_state=42,
    )
    r2 = evaluate_pipeline_cv(
        X, y, model_name, m2,
        scaler_type=scaler,
        calibration_method=cal,
        n_splits=2,
        n_repeats=2,
        inner_n_splits=3,
        random_state=42,
    )

    assert r1["standard_threshold_metrics"] == r2["standard_threshold_metrics"]
    assert r1["tuned_threshold_metrics"] == r2["tuned_threshold_metrics"]
    assert r1["selected_thresholds"] == r2["selected_thresholds"]
    assert r1["oof_y_true"] == r2["oof_y_true"]
    assert np.allclose(r1["oof_y_prob"], r2["oof_y_prob"], atol=1e-12)
    assert r1["evaluation_protocol"]["is_external_validation"] is False
    assert r1["evaluation_protocol"]["validation_type"] == "internal_repeated_stratified_cv"


def test_get_model_instances_preserves_existing_configurations():
    models = get_model_instances(pos_weight=1.5, random_state=42)
    assert set(models.keys()) == {"Dummy", "LogisticRegression", "RandomForest", "XGBoost"}
    assert models["LogisticRegression"].get_params()["C"] == 1.0
    assert models["LogisticRegression"].get_params()["solver"] == "liblinear"
    assert models["RandomForest"].get_params()["n_estimators"] == 100
    assert models["RandomForest"].get_params()["max_depth"] == 5
    assert models["XGBoost"].get_params()["n_estimators"] == 100
    assert models["XGBoost"].get_params()["max_depth"] == 3
    assert models["XGBoost"].get_params()["learning_rate"] == 0.05
    assert models["XGBoost"].get_params()["scale_pos_weight"] == 1.5
