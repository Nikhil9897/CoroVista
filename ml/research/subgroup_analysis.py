"""
CoroVista - Experiment E: Subgroup Feasibility & Disaggregated Analysis Engine
Explores model performance and calibration across patient subgroups.

Scientific Caveats:
1. Exploratory Analysis: This is exploratory demographic and clinical stratification,
   NOT a formal clinical fairness certification.
2. Sample Size Feasibility: Subgroups with N < 30 or min(N+, N-) < 5 are flagged as
   insufficient / statistically underpowered; metrics are masked as None to avoid false confidence.
3. Confounding: Differences between subgroups reflect clinical differences, sampling variability,
   and unadjusted clinical confounders, not isolated algorithmic bias.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    recall_score,
    roc_auc_score,
)

from ml.evaluation.metrics import compute_ece
from ml.research.cv_protocol import TargetCVArtifacts
from ml.research.utils import save_json, setup_plot_style

MIN_SUBGROUP_SAMPLE_SIZE = 30
MIN_MINORITY_CLASS_COUNT = 5


def identify_patient_subgroups(df_raw: pd.DataFrame) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Identifies eligible clinical and demographic subgroups from the raw dataset.
    Returns dictionary mapping category_name -> {subgroup_name -> boolean_mask}.
    """
    masks: Dict[str, Dict[str, np.ndarray]] = {}

    # 1. Biological Sex
    if "Sex" in df_raw.columns:
        sex_col = df_raw["Sex"].astype(str).str.strip().str.lower()
        is_male = sex_col.isin(["male", "m", "1"]).to_numpy()
        is_female = sex_col.isin(["fmale", "female", "f", "0"]).to_numpy()
        masks["Sex"] = {
            "Male": is_male,
            "Female": is_female,
        }

    # 2. Age Groups
    if "Age" in df_raw.columns:
        age_arr = pd.to_numeric(df_raw["Age"], errors="coerce").to_numpy()
        masks["Age Group"] = {
            "Age < 55": (age_arr < 55),
            "Age 55 - 65": ((age_arr >= 55) & (age_arr < 65)),
            "Age >= 65": (age_arr >= 65),
        }

    # 3. Diabetes Mellitus (DM)
    if "DM" in df_raw.columns:
        dm_col = df_raw["DM"].astype(str).str.strip().str.upper()
        is_dm = dm_col.isin(["Y", "YES", "1"]).to_numpy()
        masks["Diabetes (DM)"] = {
            "Diabetic": is_dm,
            "Non-Diabetic": (~is_dm),
        }

    # 4. Hypertension (HTN)
    if "HTN" in df_raw.columns:
        htn_col = df_raw["HTN"].astype(str).str.strip().str.upper()
        is_htn = htn_col.isin(["Y", "YES", "1"]).to_numpy()
        masks["Hypertension (HTN)"] = {
            "Hypertensive": is_htn,
            "Normotensive": (~is_htn),
        }

    # 5. Obesity
    if "Obesity" in df_raw.columns:
        ob_col = df_raw["Obesity"].astype(str).str.strip().str.upper()
        is_ob = ob_col.isin(["Y", "YES", "1"]).to_numpy()
        masks["Obesity"] = {
            "Obese": is_ob,
            "Non-Obese": (~is_ob),
        }

    # 6. Dyslipidemia (DLP)
    if "DLP" in df_raw.columns:
        dlp_col = df_raw["DLP"].astype(str).str.strip().str.upper()
        is_dlp = dlp_col.isin(["Y", "YES", "1"]).to_numpy()
        masks["Dyslipidemia (DLP)"] = {
            "Dyslipidemic": is_dlp,
            "Non-Dyslipidemic": (~is_dlp),
        }

    return masks


def evaluate_single_subgroup_metrics(
    y_true: np.ndarray, y_prob: np.ndarray, threshold: float
) -> Dict[str, Optional[float]]:
    """Calculates discrimination, operating, and calibration metrics for a patient partition."""
    y_pred = (y_prob >= threshold).astype(int)
    n = len(y_true)
    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    if n_pos == 0 or n_neg == 0:
        return {
            "roc_auc": None,
            "pr_auc": None,
            "sensitivity": None,
            "specificity": None,
            "balanced_accuracy": None,
            "brier_score": float(brier_score_loss(y_true, y_prob)) if n > 0 else None,
            "ece": float(compute_ece(y_true, y_prob)) if n > 0 else None,
        }

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    return {
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "pr_auc": float(average_precision_score(y_true, y_prob)),
        "sensitivity": float(recall_score(y_true, y_pred)),
        "specificity": spec,
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "ece": float(compute_ece(y_true, y_prob)),
    }


def evaluate_subgroup_analysis_for_target(
    artifacts: TargetCVArtifacts, df_raw: pd.DataFrame
) -> Dict[str, Any]:
    """
    Evaluates sample-size feasibility and performance across all candidate subgroups
    using consensus out-of-fold predicted probabilities.
    """
    threshold = artifacts.decision_threshold
    df_oof = artifacts.oof_predictions_df

    # Compute patient consensus probabilities (mean over the 5 repeats)
    pt_summary = df_oof.groupby("patient_idx").agg({
        "y_true": "first",
        "prob": "mean",
    }).sort_index()

    y_all = pt_summary["y_true"].to_numpy()
    p_all = pt_summary["prob"].to_numpy()

    subgroups = identify_patient_subgroups(df_raw)

    results_by_category: List[Dict[str, Any]] = []

    for category_name, group_dict in subgroups.items():
        cat_records = []
        for sub_name, mask in group_dict.items():
            n_sub = int(np.sum(mask))
            y_sub = y_all[mask]
            p_sub = p_all[mask]
            n_pos = int(np.sum(y_sub == 1))
            n_neg = int(np.sum(y_sub == 0))
            prev = float(n_pos / max(1, n_sub))

            is_feasible = (
                n_sub >= MIN_SUBGROUP_SAMPLE_SIZE
                and n_pos >= MIN_MINORITY_CLASS_COUNT
                and n_neg >= MIN_MINORITY_CLASS_COUNT
            )

            if is_feasible:
                m = evaluate_single_subgroup_metrics(y_sub, p_sub, threshold)
                status = "Feasible"
                infeasibility_reason = None
            else:
                m = {
                    "roc_auc": None,
                    "pr_auc": None,
                    "sensitivity": None,
                    "specificity": None,
                    "balanced_accuracy": None,
                    "brier_score": None,
                    "ece": None,
                }
                status = "Insufficient Sample / Sparse"
                reasons = []
                if n_sub < MIN_SUBGROUP_SAMPLE_SIZE:
                    reasons.append(f"Total N={n_sub} < {MIN_SUBGROUP_SAMPLE_SIZE}")
                if min(n_pos, n_neg) < MIN_MINORITY_CLASS_COUNT:
                    reasons.append(f"Minority class count {min(n_pos, n_neg)} < {MIN_MINORITY_CLASS_COUNT}")
                infeasibility_reason = "; ".join(reasons)

            cat_records.append({
                "category": category_name,
                "subgroup": sub_name,
                "sample_size": n_sub,
                "positives": n_pos,
                "negatives": n_neg,
                "prevalence": prev,
                "feasibility_status": status,
                "infeasibility_reason": infeasibility_reason,
                "metrics": m,
            })

        results_by_category.append({
            "category": category_name,
            "subgroups": cat_records,
        })

    # Overall cohort baseline metrics for context
    overall_metrics = evaluate_single_subgroup_metrics(y_all, p_all, threshold)

    return {
        "target": artifacts.target_name,
        "clinical_name": artifacts.clinical_name,
        "operating_threshold": threshold,
        "cohort_sample_size": len(y_all),
        "overall_baseline_metrics": overall_metrics,
        "categories": results_by_category,
    }


def plot_subgroup_figures(
    sub_res: Dict[str, Any], target_name: str, fig_dir: Path
) -> None:
    """Generates subgroup sample size and performance comparison charts."""
    setup_plot_style()

    # Collect all subgroups
    all_groups = []
    for cat in sub_res["categories"]:
        for g in cat["subgroups"]:
            all_groups.append(g)

    # 1. Sample Size and Positives Bar Chart
    names = [f"{g['category']}: {g['subgroup']}" for g in all_groups][::-1]
    totals = [g["sample_size"] for g in all_groups][::-1]
    positives = [g["positives"] for g in all_groups][::-1]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    y_pos = np.arange(len(names))
    ax.barh(y_pos, totals, color="#90caf9", alpha=0.8, edgecolor="#1565c0", label="Total Sample Size")
    ax.barh(y_pos, positives, color="#d32f2f", alpha=0.85, edgecolor="#b71c1c", label="Positive Cases")
    ax.axvline(MIN_SUBGROUP_SAMPLE_SIZE, color="black", linestyle="--", linewidth=1.2, label=f"Feasibility Threshold (N={MIN_SUBGROUP_SAMPLE_SIZE})")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Number of Patients", fontsize=10)
    ax.set_title(f"{target_name}: Candidate Subgroup Sample Sizes & Case Distribution", fontsize=11, fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.5)
    plt.tight_layout()
    fig.savefig(fig_dir / "subgroup_sample_sizes.png")
    plt.close(fig)

    # 2. Performance Comparison Across Feasible Subgroups (ROC-AUC & Balanced Accuracy)
    feasible_groups = [g for g in all_groups if g["feasibility_status"] == "Feasible"]
    if feasible_groups:
        f_names = [f"{g['category']}: {g['subgroup']}" for g in feasible_groups]
        f_aucs = [g["metrics"]["roc_auc"] for g in feasible_groups]
        f_bacc = [g["metrics"]["balanced_accuracy"] for g in feasible_groups]
        base_auc = sub_res["overall_baseline_metrics"]["roc_auc"]
        base_bacc = sub_res["overall_baseline_metrics"]["balanced_accuracy"]

        fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
        x = np.arange(len(f_names))
        width = 0.35

        ax.bar(x - width/2, f_aucs, width, label="Subgroup ROC-AUC", color="#1976d2", alpha=0.85, edgecolor="#0d47a1")
        ax.bar(x + width/2, f_bacc, width, label="Subgroup Balanced Accuracy", color="#388e3c", alpha=0.85, edgecolor="#1b5e20")

        if base_auc is not None:
            ax.axhline(base_auc, color="#1976d2", linestyle="--", alpha=0.7, label=f"Cohort Overall ROC-AUC ({base_auc:.3f})")
        if base_bacc is not None:
            ax.axhline(base_bacc, color="#388e3c", linestyle=":", alpha=0.7, label=f"Cohort Overall Bal Acc ({base_bacc:.3f})")

        ax.set_xticks(x)
        ax.set_xticklabels(f_names, rotation=35, ha="right", fontsize=8)
        ax.set_ylabel("Metric Value", fontsize=10)
        ax.set_ylim(0.4, 1.05)
        ax.set_title(f"{target_name}: Subgroup Performance Across Feasible Cohorts", fontsize=11, fontweight="bold")
        ax.legend(loc="lower left", fontsize=8)
        ax.grid(axis="y", alpha=0.5)
        plt.tight_layout()
        fig.savefig(fig_dir / "subgroup_performance_comparison.png")
        plt.close(fig)


def run_experiment_e_for_target(
    artifacts: TargetCVArtifacts, df_raw: pd.DataFrame, output_dir: Path
) -> Dict[str, Any]:
    """
    Executes Experiment E for a single target:
    - Identifies candidate clinical and demographic subgroups
    - Verifies sample-size feasibility with strict guards
    - Evaluates disaggregated metrics where feasible
    - Figures and JSON output
    """
    target = artifacts.target_name
    t_dir = output_dir / target.lower()
    fig_dir = t_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    sub_res = evaluate_subgroup_analysis_for_target(artifacts, df_raw)

    summary = {
        "target": target,
        "clinical_name": artifacts.clinical_name,
        "operating_threshold": artifacts.decision_threshold,
        "scientific_disclaimers": [
            "This analysis is exploratory and does NOT constitute a clinical fairness or demographic equity certification.",
            f"Sample size guards enforced: Subgroups with N < {MIN_SUBGROUP_SAMPLE_SIZE} or min(N+, N-) < {MIN_MINORITY_CLASS_COUNT} are flagged as statistically underpowered, and metrics are masked as None.",
            "Observed metric differences between subgroups reflect clinical heterogeneity, sample size limitations, and unadjusted confounders rather than isolated model bias.",
        ],
        "subgroup_feasibility_and_performance": sub_res,
    }

    json_path = t_dir / f"{target.lower()}_subgroup_analysis.json"
    save_json(summary, json_path)

    plot_subgroup_figures(sub_res, target, fig_dir)

    return summary
