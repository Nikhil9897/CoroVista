"""
CoroVista - Experiment D: Robustness, Sensitivity & Feature Ablation Engine
Evaluates model behavior under controlled input feature perturbations,
pipeline missingness stress tests, and inside-CV feature group ablations.

Research Questions:
1. Which features produce the largest prediction shifts under controlled numerical perturbation?
2. How resilient are classification decisions to plausible categorical substitutions?
3. How does the preprocessing imputer perform under synthetic missingness stress tests?
4. What is the predictive contribution of distinct clinical domains (ECG, Echo, Labs, Demographics)?
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler

from ml.preprocessing.feature_metadata import FEATURE_PARTITIONS
from ml.preprocessing.pipeline import (
    ClinicalFeatureCleaner,
    LeakageGuardTransformer,
    extract_features_and_targets,
)
from ml.research.cv_protocol import (
    APPROVED_TARGET_CONFIGS,
    TargetCVArtifacts,
    get_base_estimator,
)
from ml.research.utils import save_json, setup_plot_style
from ml.training.benchmark import _extract_positive_probs, _prepare_fold_estimator

NUMERICAL_FEATURES: List[str] = [
    "Age", "Weight", "Length", "BMI", "BP", "PR", "FBS", "CR", "TG", "LDL", "HDL",
    "BUN", "ESR", "HB", "K", "Na", "WBC", "Lymph", "Neut", "PLT", "EF-TTE", "Function Class",
]

INTEGER_NUMERICAL_FEATURES: set[str] = {
    "Age", "Weight", "Length", "BP", "PR", "FBS", "TG", "LDL", "BUN", "ESR",
    "WBC", "Lymph", "Neut", "PLT", "EF-TTE", "Function Class",
}

BINARY_FEATURES_TO_TEST: List[str] = [
    "Sex", "DM", "HTN", "Current Smoker", "EX-Smoker", "FH", "Obesity",
    "Typical Chest Pain", "Dyspnea", "Atypical", "Nonanginal", "LowTH Ang",
    "Q Wave", "St Elevation", "St Depression", "Tinversion", "LVH", "Poor R Progression",
]

CLINICAL_ABLATION_GROUPS: Dict[str, List[str]] = {
    "Demographics": ["Age", "Weight", "Length", "Sex", "BMI"],
    "History & Habits": [
        "DM", "HTN", "Current Smoker", "EX-Smoker", "FH", "Obesity", "CRF", "CVA",
        "Airway disease", "Thyroid Disease", "CHF", "DLP",
    ],
    "Symptoms & Exam": [
        "BP", "PR", "Edema", "Weak Peripheral Pulse", "Lung rales", "Systolic Murmur",
        "Diastolic Murmur", "Typical Chest Pain", "Dyspnea", "Function Class",
        "Atypical", "Nonanginal", "LowTH Ang",
    ],
    "12-Lead ECG": [
        "Q Wave", "St Elevation", "St Depression", "Tinversion", "LVH", "Poor R Progression", "BBB",
    ],
    "Laboratory": [
        "FBS", "CR", "TG", "LDL", "HDL", "BUN", "ESR", "HB", "K", "Na", "WBC", "Lymph", "Neut", "PLT",
    ],
    "Echocardiography": ["EF-TTE", "Region RWMA", "VHD"],
}

KEY_SINGLE_ABLATIONS: List[str] = [
    "Region RWMA",
    "Typical Chest Pain",
    "Age",
    "EF-TTE",
]


def evaluate_numerical_perturbation(
    artifacts: TargetCVArtifacts,
    df_raw: pd.DataFrame,
    perturbation_scales: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Applies controlled additive perturbations (+- scale * sigma) to continuous numerical features.
    Guarantees:
    - Sigma and bounds are estimated strictly from training data.
    - Clamped to observed physiological ranges [min, max].
    - Valid integer datatypes preserved where appropriate.
    - Measures mean absolute probability shift |Delta p| and classification flip rate.
    """
    if perturbation_scales is None:
        perturbation_scales = [0.1, 0.5, 1.0]

    X, _ = extract_features_and_targets(df_raw)
    threshold = artifacts.decision_threshold
    fold_models = artifacts.fold_models[:5]  # Use first 5 outer fold models for efficiency

    # Compute baseline statistics strictly across training population
    num_stats = {}
    for col in NUMERICAL_FEATURES:
        if col in X.columns:
            vals = pd.to_numeric(X[col], errors="coerce").dropna()
            num_stats[col] = {
                "mean": float(vals.mean()),
                "std": float(vals.std()),
                "min": float(vals.min()),
                "max": float(vals.max()),
                "is_int": col in INTEGER_NUMERICAL_FEATURES,
            }

    feature_results = []

    for feat, stats_dict in num_stats.items():
        feat_std = stats_dict["std"]
        feat_min = stats_dict["min"]
        feat_max = stats_dict["max"]
        is_int = stats_dict["is_int"]

        scale_metrics = {}

        for scale in perturbation_scales:
            delta = scale * feat_std
            abs_diffs_pos: List[float] = []
            abs_diffs_neg: List[float] = []
            flips_pos = 0
            flips_neg = 0
            total_evals = 0

            for model in fold_models:
                base_probs = _extract_positive_probs(model, X)
                base_preds = (base_probs >= threshold).astype(int)

                # Positive perturbation (+delta)
                X_pos = X.copy()
                val_pos = pd.to_numeric(X_pos[feat], errors="coerce") + delta
                val_pos = np.clip(val_pos, feat_min, feat_max)
                if is_int:
                    val_pos = np.round(val_pos).astype(int)
                X_pos[feat] = val_pos

                pos_probs = _extract_positive_probs(model, X_pos)
                pos_preds = (pos_probs >= threshold).astype(int)

                abs_diffs_pos.extend(np.abs(pos_probs - base_probs).tolist())
                flips_pos += int(np.sum(pos_preds != base_preds))

                # Negative perturbation (-delta)
                X_neg = X.copy()
                val_neg = pd.to_numeric(X_neg[feat], errors="coerce") - delta
                val_neg = np.clip(val_neg, feat_min, feat_max)
                if is_int:
                    val_neg = np.round(val_neg).astype(int)
                X_neg[feat] = val_neg

                neg_probs = _extract_positive_probs(model, X_neg)
                neg_preds = (neg_probs >= threshold).astype(int)

                abs_diffs_neg.extend(np.abs(neg_probs - base_probs).tolist())
                flips_neg += int(np.sum(neg_preds != base_preds))

                total_evals += len(X)

            mean_delta_p = float(np.mean(abs_diffs_pos + abs_diffs_neg))
            flip_rate = float((flips_pos + flips_neg) / (2 * max(1, total_evals)))

            scale_metrics[f"scale_{scale}"] = {
                "mean_abs_prob_shift": mean_delta_p,
                "flip_rate": flip_rate,
            }

        feature_results.append({
            "feature": feat,
            "training_std": feat_std,
            "min_val": feat_min,
            "max_val": feat_max,
            "sensitivity_moderate_0_5_sigma": scale_metrics["scale_0.5"]["mean_abs_prob_shift"],
            "flip_rate_moderate_0_5_sigma": scale_metrics["scale_0.5"]["flip_rate"],
            "scales": scale_metrics,
        })

    # Sort descending by sensitivity at moderate 0.5 sigma perturbation
    feature_results.sort(key=lambda x: x["sensitivity_moderate_0_5_sigma"], reverse=True)

    return {
        "perturbation_scales": perturbation_scales,
        "features_evaluated_count": len(feature_results),
        "feature_sensitivities": feature_results,
    }


def evaluate_categorical_robustness(
    artifacts: TargetCVArtifacts, df_raw: pd.DataFrame
) -> Dict[str, Any]:
    """
    Evaluates prediction and classification shift under valid category substitutions:
    - Sex (Male <-> Female)
    - VHD (adjacent severity step)
    - Binary clinical variables (0 <-> 1)
    """
    X, _ = extract_features_and_targets(df_raw)
    threshold = artifacts.decision_threshold
    fold_models = artifacts.fold_models[:5]

    cat_results = []

    # 1. Binary Features Flip Test
    for feat in BINARY_FEATURES_TO_TEST:
        if feat not in X.columns:
            continue

        abs_diffs: List[float] = []
        flips = 0
        total_evals = 0

        for model in fold_models:
            base_probs = _extract_positive_probs(model, X)
            base_preds = (base_probs >= threshold).astype(int)

            X_flipped = X.copy()
            # Handle Sex ('Male' <-> 'Fmale')
            if feat == "Sex":
                X_flipped["Sex"] = X_flipped["Sex"].map(
                    lambda s: "Fmale" if str(s).strip().lower() in ["male", "m", "1"] else "Male"
                )
            else:
                # Handle 'Y'/'N' string or numeric binary
                if pd.api.types.is_numeric_dtype(X_flipped[feat]):
                    X_flipped[feat] = 1 - X_flipped[feat].fillna(0).astype(int)
                else:
                    X_flipped[feat] = X_flipped[feat].astype(str).str.strip().map(
                        lambda s: "N" if str(s).upper() in ["Y", "YES", "1"] else "Y"
                    )

            flip_probs = _extract_positive_probs(model, X_flipped)
            flip_preds = (flip_probs >= threshold).astype(int)

            abs_diffs.extend(np.abs(flip_probs - base_probs).tolist())
            flips += int(np.sum(flip_preds != base_preds))
            total_evals += len(X)

        cat_results.append({
            "feature": feat,
            "perturbation_type": "Binary Substitution (0 <-> 1)",
            "mean_abs_prob_shift": float(np.mean(abs_diffs)),
            "flip_rate": float(flips / max(1, total_evals)),
        })

    # 2. VHD adjacent severity step (Normal -> Mild -> Moderate -> Severe)
    vhd_step_map = {
        "Normal": "Mild", "N": "Mild", "normal": "Mild",
        "Mild": "Moderate", "mild": "Moderate",
        "Moderate": "Severe", "moderate": "Severe",
        "Severe": "Moderate", "severe": "Moderate",
    }
    abs_diffs_vhd: List[float] = []
    flips_vhd = 0
    total_evals_vhd = 0

    for model in fold_models:
        base_probs = _extract_positive_probs(model, X)
        base_preds = (base_probs >= threshold).astype(int)

        X_vhd = X.copy()
        X_vhd["VHD"] = X_vhd["VHD"].astype(str).str.strip().map(vhd_step_map).fillna("Mild")
        vhd_probs = _extract_positive_probs(model, X_vhd)
        vhd_preds = (vhd_probs >= threshold).astype(int)

        abs_diffs_vhd.extend(np.abs(vhd_probs - base_probs).tolist())
        flips_vhd += int(np.sum(vhd_preds != base_preds))
        total_evals_vhd += len(X)

    cat_results.append({
        "feature": "VHD",
        "perturbation_type": "Adjacent Severity Grade Shift",
        "mean_abs_prob_shift": float(np.mean(abs_diffs_vhd)),
        "flip_rate": float(flips_vhd / max(1, total_evals_vhd)),
    })

    cat_results.sort(key=lambda x: x["mean_abs_prob_shift"], reverse=True)

    return {
        "categorical_substitutions_count": len(cat_results),
        "results": cat_results,
    }


def evaluate_missingness_stress_test(
    artifacts: TargetCVArtifacts,
    df_raw: pd.DataFrame,
    missing_rates: Optional[List[float]] = None,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Stress-tests the preprocessing defensive SimpleImputer behavior under MCAR missingness.
    Discloses that the audited dataset has zero missing values, so this is a defensive pipeline
    verification rather than real-world missingness evidence.
    """
    if missing_rates is None:
        missing_rates = [0.05, 0.10, 0.20, 0.30]

    X, targets = extract_features_and_targets(df_raw)
    y = targets[artifacts.target_name]
    y_arr = np.asarray(y)
    fold_models = artifacts.fold_models[:5]
    rng = np.random.RandomState(random_state)

    stress_results = []

    for rate in missing_rates:
        roc_aucs: List[float] = []
        pr_aucs: List[float] = []
        briers: List[float] = []
        abs_diffs: List[float] = []

        for model in fold_models:
            base_probs = _extract_positive_probs(model, X)

            # Introduce MCAR missingness mask
            X_miss = X.copy()
            mask = rng.rand(*X_miss.shape) < rate
            X_miss = X_miss.mask(mask, np.nan)

            miss_probs = _extract_positive_probs(model, X_miss)

            roc_aucs.append(float(roc_auc_score(y_arr, miss_probs)))
            pr_aucs.append(float(average_precision_score(y_arr, miss_probs)))
            briers.append(float(brier_score_loss(y_arr, miss_probs)))
            abs_diffs.extend(np.abs(miss_probs - base_probs).tolist())

        stress_results.append({
            "missingness_rate": rate,
            "roc_auc_mean": float(np.mean(roc_aucs)),
            "roc_auc_std": float(np.std(roc_aucs)),
            "pr_auc_mean": float(np.mean(pr_aucs)),
            "pr_auc_std": float(np.std(pr_aucs)),
            "brier_score_mean": float(np.mean(briers)),
            "brier_score_std": float(np.std(briers)),
            "mean_abs_probability_drift": float(np.mean(abs_diffs)),
        })

    return {
        "audited_dataset_missing_count": 0,
        "methodological_note": (
            "The audited Z-Alizadeh Sani cohort contains zero missing values. "
            "This experiment represents a synthetic stress test of the preprocessing pipeline's "
            "defensive SimpleImputer behavior under MCAR conditions, not real-world missingness."
        ),
        "results": stress_results,
    }


def build_ablation_model(
    drop_cols: List[str],
    model_family: str,
    scaler_type: str,
    vhd_encoding: str,
    calibration_method: Optional[str],
    seed: int,
) -> Any:
    """Builds a leakage-safe pipeline that selectively excludes ablated features."""
    active_num_cols = [c for c in FEATURE_PARTITIONS["numerical"] if c not in drop_cols]
    if "Function Class" not in drop_cols:
        active_num_cols.append("Function Class")

    active_bin_cols = [
        c for c in list(FEATURE_PARTITIONS["binary_integer"]) + list(FEATURE_PARTITIONS["binary_string"])
        if c not in drop_cols
    ]
    if "Sex" not in drop_cols:
        active_bin_cols.append("Sex")

    categorical_cols = ["BBB"]
    if vhd_encoding == "onehot":
        categorical_cols.append("VHD")
    categorical_cols = [c for c in categorical_cols if c not in drop_cols]

    transformers = []
    if active_num_cols:
        num_steps = [("imputer", SimpleImputer(strategy="median"))]
        if scaler_type == "standard":
            num_steps.append(("scaler", StandardScaler()))
        elif scaler_type == "robust":
            num_steps.append(("scaler", RobustScaler()))
        transformers.append(("num", Pipeline(num_steps), active_num_cols))

    if active_bin_cols:
        transformers.append(("bin", Pipeline([("imputer", SimpleImputer(strategy="most_frequent"))]), active_bin_cols))

    if categorical_cols:
        transformers.append(("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False)),
        ]), categorical_cols))

    col_proc = ColumnTransformer(transformers=transformers, remainder="drop")
    prep_pipe = Pipeline([
        ("leakage_guard", LeakageGuardTransformer()),
        ("cleaner", ClinicalFeatureCleaner(vhd_encoding=vhd_encoding, drop_zero_variance=True)),
        ("processor", col_proc),
    ])

    base_est = get_base_estimator(model_family, random_state=seed)
    model = _prepare_fold_estimator(base_est, model_family)

    full_pipe = Pipeline([
        ("preprocessing", prep_pipe),
        ("classifier", model),
    ])

    if calibration_method and model_family != "Dummy":
        cal_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
        return CalibratedClassifierCV(estimator=full_pipe, method=calibration_method, cv=cal_cv)

    return full_pipe


def evaluate_feature_ablation_cv(
    target_name: str,
    df_raw: pd.DataFrame,
    n_splits: int = 5,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Performs leakage-safe feature ablation inside 5-fold cross-validation.
    Features are dropped inside training partitions before fitting.
    Evaluates clinical domain groups and key individual features.
    """
    config = dict(APPROVED_TARGET_CONFIGS[target_name])
    X, targets = extract_features_and_targets(df_raw)
    y = targets[target_name]
    y_arr = np.asarray(y)

    model_family = config["model_family"]
    scaler_type = config["scaler_type"]
    vhd_encoding = config["vhd_encoding"]
    calibration_method = config["calibration_method"]
    threshold = float(config["decision_threshold"])

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    def _evaluate_folds(drop_cols: List[str]) -> Dict[str, float]:
        oof_probs = np.zeros(len(X), dtype=float)

        for fold_idx, (tr_idx, te_idx) in enumerate(skf.split(X, y)):
            X_tr, X_te = X.iloc[tr_idx], X.iloc[te_idx]
            y_tr = y.iloc[tr_idx]

            fold_model = build_ablation_model(
                drop_cols=drop_cols,
                model_family=model_family,
                scaler_type=scaler_type,
                vhd_encoding=vhd_encoding,
                calibration_method=calibration_method,
                seed=random_state + fold_idx,
            )
            fold_model.fit(X_tr, y_tr)
            oof_probs[te_idx] = _extract_positive_probs(fold_model, X_te)

        oof_preds = (oof_probs >= threshold).astype(int)
        return {
            "roc_auc": float(roc_auc_score(y_arr, oof_probs)),
            "pr_auc": float(average_precision_score(y_arr, oof_probs)),
            "brier": float(brier_score_loss(y_arr, oof_probs)),
            "recall": float(recall_score(y_arr, oof_preds)),
            "balanced_accuracy": float(balanced_accuracy_score(y_arr, oof_preds)),
        }

    # 1. Baseline metrics (Full feature set)
    baseline_metrics = _evaluate_folds(drop_cols=[])

    ablation_items: List[Tuple[str, str, List[str]]] = []
    # Add domain groups
    for group_name, cols in CLINICAL_ABLATION_GROUPS.items():
        ablation_items.append((group_name, "Domain Group", cols))
    # Add single features
    for single_col in KEY_SINGLE_ABLATIONS:
        ablation_items.append((single_col, "Single Feature", [single_col]))

    ablation_results = []

    for name, kind, cols in ablation_items:
        m = _evaluate_folds(drop_cols=cols)
        ablation_results.append({
            "ablation_name": name,
            "ablation_type": kind,
            "features_removed": cols,
            "features_removed_count": len(cols),
            "roc_auc": m["roc_auc"],
            "delta_roc_auc": float(m["roc_auc"] - baseline_metrics["roc_auc"]),
            "pr_auc": m["pr_auc"],
            "delta_pr_auc": float(m["pr_auc"] - baseline_metrics["pr_auc"]),
            "brier_score": m["brier"],
            "delta_brier": float(m["brier"] - baseline_metrics["brier"]),
            "recall": m["recall"],
            "delta_recall": float(m["recall"] - baseline_metrics["recall"]),
            "balanced_accuracy": m["balanced_accuracy"],
            "delta_balanced_accuracy": float(m["balanced_accuracy"] - baseline_metrics["balanced_accuracy"]),
        })

    # Sort descending by delta ROC-AUC degradation (most detrimental removal first)
    ablation_results.sort(key=lambda x: x["delta_roc_auc"])

    return {
        "target": target_name,
        "baseline_metrics": baseline_metrics,
        "ablations": ablation_results,
    }


def plot_robustness_figures(
    num_res: Dict[str, Any],
    cat_res: Dict[str, Any],
    miss_res: Dict[str, Any],
    abl_res: Dict[str, Any],
    target_name: str,
    fig_dir: Path,
) -> None:
    """Generates sensitivity rankings, categorical flips, missingness, and ablation charts."""
    setup_plot_style()

    # 1. Numerical Sensitivity Bar Chart (Top 12)
    top_num = num_res["feature_sensitivities"][:12]
    feats = [item["feature"] for item in top_num][::-1]
    shifts = [item["sensitivity_moderate_0_5_sigma"] for item in top_num][::-1]

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    y_pos = np.arange(len(feats))
    ax.barh(y_pos, shifts, color="#1976d2", alpha=0.85, edgecolor="#0d47a1")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feats, fontsize=9)
    ax.set_xlabel("Mean Absolute Probability Shift |Δp| (at 0.5 σ perturbation)", fontsize=10)
    ax.set_title(f"{target_name}: Numerical Feature Perturbation Sensitivity (Top 12)", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.5)
    plt.tight_layout()
    fig.savefig(fig_dir / "numerical_perturbation_sensitivity.png")
    plt.close(fig)

    # 2. Categorical Substitution Flip Rate Bar Chart
    top_cat = cat_res["results"][:10]
    cat_feats = [item["feature"] for item in top_cat][::-1]
    cat_flips = [item["flip_rate"] * 100 for item in top_cat][::-1]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    y_pos = np.arange(len(cat_feats))
    ax.barh(y_pos, cat_flips, color="#e65100", alpha=0.85, edgecolor="#bf360c")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_feats, fontsize=9)
    ax.set_xlabel("Classification Label Flip Rate (%) Under Category Substitution", fontsize=10)
    ax.set_title(f"{target_name}: Categorical Robustness & Decision Flip Rate", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.5)
    plt.tight_layout()
    fig.savefig(fig_dir / "categorical_flip_rates.png")
    plt.close(fig)

    # 3. Missingness Stress Test Curve
    rates = [m["missingness_rate"] * 100 for m in miss_res["results"]]
    aucs = [m["roc_auc_mean"] for m in miss_res["results"]]
    drifts = [m["mean_abs_probability_drift"] for m in miss_res["results"]]

    fig, ax1 = plt.subplots(figsize=(7, 4.5), dpi=300)
    color = "#1f77b4"
    ax1.set_xlabel("Synthetic MCAR Missingness Proportion (%)", fontsize=10)
    ax1.set_ylabel("ROC-AUC", color=color, fontsize=10)
    ax1.plot(rates, aucs, marker="o", color=color, linewidth=2, label="ROC-AUC")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(True, alpha=0.5)

    ax2 = ax1.twinx()
    color = "#d9534f"
    ax2.set_ylabel("Mean Probability Drift |Δp|", color=color, fontsize=10)
    ax2.plot(rates, drifts, marker="s", color=color, linewidth=2, linestyle="--", label="Mean |Δp|")
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title(f"{target_name}: Pipeline Missingness Stress Test Degradation", fontsize=11, fontweight="bold")
    plt.tight_layout()
    fig.savefig(fig_dir / "missingness_stress_test.png")
    plt.close(fig)

    # 4. Feature Ablation Delta ROC-AUC Bar Chart
    abls = abl_res["ablations"]
    abl_names = [a["ablation_name"] for a in abls]
    delta_aucs = [a["delta_roc_auc"] for a in abls]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    y_pos = np.arange(len(abl_names))
    colors = ["#d32f2f" if d < -0.01 else "#388e3c" if d > 0.01 else "#757575" for d in delta_aucs]
    ax.barh(y_pos, delta_aucs, color=colors, alpha=0.85, edgecolor="#333333")
    ax.axvline(0, color="black", linestyle="-", linewidth=1.0)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(abl_names, fontsize=9)
    ax.set_xlabel("Δ ROC-AUC (Ablated Model minus Baseline)", fontsize=10)
    ax.set_title(f"{target_name}: Inside-CV Feature Ablation Impact", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.5)
    plt.tight_layout()
    fig.savefig(fig_dir / "feature_ablation_comparison.png")
    plt.close(fig)


def run_experiment_d_for_target(
    artifacts: TargetCVArtifacts, df_raw: pd.DataFrame, output_dir: Path
) -> Dict[str, Any]:
    """
    Executes Experiment D for a single target:
    - Numerical perturbation sensitivity
    - Categorical substitution robustness
    - Missingness stress testing
    - Inside-CV feature ablation
    - Figures and JSON output
    """
    target = artifacts.target_name
    t_dir = output_dir / target.lower()
    fig_dir = t_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    num_res = evaluate_numerical_perturbation(artifacts, df_raw)
    cat_res = evaluate_categorical_robustness(artifacts, df_raw)
    miss_res = evaluate_missingness_stress_test(artifacts, df_raw)
    abl_res = evaluate_feature_ablation_cv(target, df_raw, n_splits=5)

    summary = {
        "target": target,
        "clinical_name": artifacts.clinical_name,
        "model_family": artifacts.model_family,
        "operating_threshold": artifacts.decision_threshold,
        "numerical_perturbation": num_res,
        "categorical_robustness": cat_res,
        "missingness_stress_test": miss_res,
        "feature_ablation": abl_res,
    }

    json_path = t_dir / f"{target.lower()}_robustness_summary.json"
    save_json(summary, json_path)

    plot_robustness_figures(num_res, cat_res, miss_res, abl_res, target, fig_dir)

    return summary
