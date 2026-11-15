"""
CoroVista - ML Evaluation Metrics & Calibration Utilities
Stage 2: Machine Learning Foundation

Provides validated evaluation functions for:
- Classification metrics: ROC-AUC, PR-AUC, Accuracy, Precision, Recall, F1, Balanced Accuracy
- Probability calibration: Brier Score, Expected Calibration Error (ECE)
- Threshold optimization strictly on validation / inner out-of-fold predictions
- Repeated-CV fold summary aggregation (internal validation only; folds are not
  independent datasets and do not substitute for external validation)
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

SUPPORTED_THRESHOLD_METRICS: Tuple[str, ...] = ("f1", "youden")


def _validate_binary_inputs(
    y_true: Any,
    y_prob: Any,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Validates binary targets and predicted probabilities.

    Ensures:
    - Both inputs are 1-dimensional, non-empty, and of equal length.
    - y_true contains only finite binary values {0, 1}.
    - y_prob contains only finite probabilities within [0.0, 1.0].
    """
    y_true_arr = np.asarray(y_true)
    y_prob_arr = np.asarray(y_prob)

    if y_true_arr.ndim != 1 or y_prob_arr.ndim != 1:
        raise ValueError(
            f"y_true and y_prob must be 1D arrays; got shapes {y_true_arr.shape} and {y_prob_arr.shape}."
        )

    if len(y_true_arr) != len(y_prob_arr):
        raise ValueError(
            f"Length mismatch between y_true ({len(y_true_arr)}) and y_prob ({len(y_prob_arr)})."
        )

    if len(y_true_arr) == 0:
        raise ValueError("y_true and y_prob must not be empty.")

    if y_true_arr.dtype == bool:
        y_true_num = y_true_arr.astype(float)
    else:
        try:
            y_true_num = y_true_arr.astype(float)
        except (TypeError, ValueError) as exc:
            raise ValueError("y_true must contain numeric binary labels {0, 1}.") from exc

    if not np.isfinite(y_true_num).all():
        raise ValueError("y_true contains non-finite values (NaN or Inf).")

    unique_vals = set(np.unique(y_true_num).tolist())
    if not unique_vals.issubset({0.0, 1.0}):
        raise ValueError(
            f"y_true must contain only binary values {{0, 1}}; got {sorted(unique_vals)}."
        )

    try:
        y_prob_float = y_prob_arr.astype(float)
    except (TypeError, ValueError) as exc:
        raise ValueError("y_prob must contain numeric probabilities within [0.0, 1.0].") from exc

    if not np.isfinite(y_prob_float).all():
        raise ValueError("y_prob contains non-finite values (NaN or Inf).")

    if (y_prob_float < 0.0).any() or (y_prob_float > 1.0).any():
        raise ValueError(
            f"y_prob values must be within [0.0, 1.0]; got range [{float(np.min(y_prob_float))}, {float(np.max(y_prob_float))}]."
        )

    return y_true_num.astype(int), y_prob_float


def _validate_threshold(threshold: float) -> float:
    """Validates that the classification threshold is a finite numeric float in [0.0, 1.0]."""
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float, np.integer, np.floating)):
        raise ValueError(
            f"threshold must be a finite float in [0.0, 1.0], got {type(threshold).__name__} ({threshold!r})."
        )
    thresh = float(threshold)
    if not np.isfinite(thresh) or thresh < 0.0 or thresh > 1.0:
        raise ValueError(f"threshold must be a finite float within [0.0, 1.0], got {threshold!r}.")
    return thresh


def _validate_threshold_metric(metric: str) -> str:
    """Validates that the threshold optimization metric is explicitly supported."""
    if not isinstance(metric, str) or metric not in SUPPORTED_THRESHOLD_METRICS:
        raise ValueError(
            f"Unsupported threshold optimization metric {metric!r}. "
            f"Supported metrics: {SUPPORTED_THRESHOLD_METRICS}."
        )
    return metric


def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Computes primary and secondary evaluation metrics given ground truth
    and predicted probabilities.

    When y_true contains only a single class (all 0s or all 1s), ranking-based
    discrimination metrics (`roc_auc` and `pr_auc`) are mathematically undefined
    and returned explicitly as `None` rather than substituted with `0.5` or
    class prevalence.
    """
    y_true_arr, y_prob_arr = _validate_binary_inputs(y_true, y_prob)
    thresh = _validate_threshold(threshold)
    y_pred = (y_prob_arr >= thresh).astype(int)

    unique_classes = np.unique(y_true_arr)
    has_both_classes = len(unique_classes) == 2

    # Primary ranking discrimination metrics (undefined for single-class y_true)
    if has_both_classes:
        roc_auc: Optional[float] = round(float(roc_auc_score(y_true_arr, y_prob_arr)), 4)
        pr_auc: Optional[float] = round(float(average_precision_score(y_true_arr, y_prob_arr)), 4)
    else:
        roc_auc = None
        pr_auc = None

    # Secondary threshold-dependent classification metrics
    acc = float(accuracy_score(y_true_arr, y_pred))
    prec = float(precision_score(y_true_arr, y_pred, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred, zero_division=0))
    if has_both_classes:
        bal_acc = float(balanced_accuracy_score(y_true_arr, y_pred))
    else:
        # For single-class ground truth, balanced accuracy reduces to accuracy on the present class
        bal_acc = acc

    # Calibration metrics
    brier = float(brier_score_loss(y_true_arr, y_prob_arr))
    ece = compute_ece(y_true_arr, y_prob_arr, n_bins=10)

    # Fixed [0, 1] label matrix prevents shape (1, 1) unpacking failure on degenerate splits
    cm = confusion_matrix(y_true_arr, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "brier_score": round(brier, 4),
        "ece": round(ece, 4),
        "threshold": round(thresh, 3),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE) using equal-width uniform bins over [0, 1].

    Methodological Notes on Binning Dependence:
    - ECE partitions predicted probabilities into `n_bins` equal-width intervals
      ([0, 1/n_bins), ..., [(n_bins-1)/n_bins, 1]).
    - Empirical ECE values depend directly on `n_bins` and the binning scheme
      (uniform width vs. equal-mass/quantile adaptive binning).
    - In small-sample validation folds (e.g., ~60 patients per fold in 5-fold CV
      on N=303), sparse bins can exhibit elevated finite-sample estimation variance,
      and empty bins contribute zero weight.
    """
    y_true_arr, y_prob_arr = _validate_binary_inputs(y_true, y_prob)
    if isinstance(n_bins, bool) or not isinstance(n_bins, int) or n_bins < 1:
        raise ValueError(f"n_bins must be a positive integer >= 1, got {n_bins!r}.")

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true_arr)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        mask = (
            (y_prob_arr >= bin_lower) & (y_prob_arr < bin_upper)
            if i < n_bins - 1
            else (y_prob_arr >= bin_lower) & (y_prob_arr <= bin_upper)
        )
        bin_count = int(np.sum(mask))

        if bin_count > 0:
            bin_acc = float(np.mean(y_true_arr[mask]))
            bin_conf = float(np.mean(y_prob_arr[mask]))
            ece += (bin_count / n) * abs(bin_acc - bin_conf)

    return float(ece)


def find_optimal_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    metric: str = "f1",
) -> float:
    """
    Finds optimal classification threshold strictly on training/inner-OOF validation
    predictions. Never call this function on outer test fold labels or predictions.

    Supported metric options:
    - 'f1': Maximizes F1-score (with zero_division=0).
    - 'youden': Maximizes Youden's J statistic (sensitivity + specificity - 1).

    Returns 0.5 safely if y_true contains fewer than two distinct classes.
    """
    y_true_arr, y_prob_arr = _validate_binary_inputs(y_true, y_prob)
    selected_metric = _validate_threshold_metric(metric)

    if len(np.unique(y_true_arr)) < 2:
        return 0.5

    thresholds = np.linspace(0.15, 0.85, 71)
    best_thresh = 0.5
    best_score = -float("inf")

    for t in thresholds:
        y_pred = (y_prob_arr >= t).astype(int)
        if selected_metric == "f1":
            score = float(f1_score(y_true_arr, y_pred, zero_division=0))
        elif selected_metric == "youden":
            rec = float(recall_score(y_true_arr, y_pred, zero_division=0))
            tn, fp, _, _ = confusion_matrix(y_true_arr, y_pred, labels=[0, 1]).ravel()
            spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
            score = rec + spec - 1.0
        else:
            raise ValueError(f"Unsupported threshold optimization metric: {selected_metric!r}")

        if score > best_score:
            best_score = score
            best_thresh = float(t)

    return float(round(best_thresh, 3))


def aggregate_cv_metrics(fold_metrics_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Computes repeated-CV fold summaries (mean and standard deviation across folds).

    Statistical Reporting Scope:
    - Repeated k-fold cross-validation (e.g., 5 folds x 5 repeats = 25 fold evaluations)
      reuses the same patient cohort across repeats.
    - Fold evaluations are NOT independent datasets or independent experiments.
    - This function intentionally reports descriptive fold mean/SD and valid-fold counts
      rather than naive confidence intervals (e.g., mean +/- 1.96 * SD / sqrt(25))
      that falsely assume fold independence.
    - Repeated CV is internal validation only and does not constitute external validation.
    - Undefined fold metrics (None, e.g., single-class ROC-AUC/PR-AUC) are excluded from
      the numeric mean/SD and tracked via `n_valid_folds` and `n_undefined_folds`.
    """
    keys = [
        "roc_auc",
        "pr_auc",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "balanced_accuracy",
        "brier_score",
        "ece",
    ]
    summary: Dict[str, Dict[str, Any]] = {}
    for k in keys:
        present = [m[k] for m in fold_metrics_list if k in m]
        if not present:
            continue
        valid_vals = [float(v) for v in present if v is not None]
        n_total = len(present)
        n_valid = len(valid_vals)
        n_undefined = n_total - n_valid

        if valid_vals:
            summary[k] = {
                "mean": round(float(np.mean(valid_vals)), 4),
                "std": round(float(np.std(valid_vals)), 4),
                "n_valid_folds": n_valid,
                "n_undefined_folds": n_undefined,
                "summary_scope": "repeated_cv_fold_summary",
            }
        else:
            summary[k] = {
                "mean": None,
                "std": None,
                "n_valid_folds": 0,
                "n_undefined_folds": n_undefined,
                "summary_scope": "repeated_cv_fold_summary",
            }
    return summary
