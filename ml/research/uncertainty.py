"""
CoroVista - Experiment C: Predictive Uncertainty Estimation Engine
Investigates the reliability and structure of model uncertainty.

Scientific Distinctions:
1. Predictive Probability: P(Y=1|X)
2. Across-Model Empirical Variability: Var_F(P(Y=1|X)) across training partitions
3. Predictive Uncertainty: Binary Entropy H(P) and Margin |P - tau|
4. Calibration Error: Deviation of empirical frequency from predicted probability
"""

from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from ml.research.cv_protocol import TargetCVArtifacts
from ml.research.utils import compute_binary_entropy, save_json, setup_plot_style


def evaluate_uncertainty_metrics(artifacts: TargetCVArtifacts) -> Dict[str, Any]:
    """
    Evaluates empirical fold variability, binary entropy, margin-based uncertainty,
    and their empirical relationship with classification errors and probability calibration.
    """
    df_oof = artifacts.oof_predictions_df
    threshold = artifacts.decision_threshold
    patients = sorted(df_oof["patient_idx"].unique())
    n_patients = len(patients)

    patient_records: List[Dict[str, Any]] = []

    all_means: List[float] = []
    all_sds: List[float] = []
    all_q10: List[float] = []
    all_q90: List[float] = []
    all_entropies: List[float] = []
    all_margins: List[float] = []
    all_errors: List[int] = []

    correct_entropies: List[float] = []
    incorrect_entropies: List[float] = []
    correct_margins: List[float] = []
    incorrect_margins: List[float] = []

    for pt in patients:
        sub = df_oof[df_oof["patient_idx"] == pt]
        probs = sub["prob"].to_numpy()
        y_true = int(sub["y_true"].iloc[0])

        p_mean = float(np.mean(probs))
        p_std = float(np.std(probs))
        p_q10 = float(np.percentile(probs, 10))
        p_q90 = float(np.percentile(probs, 90))

        # Binary entropy evaluated on the consensus out-of-fold probability
        h_entropy = float(compute_binary_entropy(p_mean))

        # Margin from the decision threshold
        margin = float(abs(p_mean - threshold))

        # Consensus prediction based on mean probability
        consensus_pred = int(p_mean >= threshold)
        is_error = int(consensus_pred != y_true)

        all_means.append(p_mean)
        all_sds.append(p_std)
        all_q10.append(p_q10)
        all_q90.append(p_q90)
        all_entropies.append(h_entropy)
        all_margins.append(margin)
        all_errors.append(is_error)

        if is_error:
            incorrect_entropies.append(h_entropy)
            incorrect_margins.append(margin)
        else:
            correct_entropies.append(h_entropy)
            correct_margins.append(margin)

        patient_records.append({
            "patient_idx": int(pt),
            "y_true": y_true,
            "mean_prob": p_mean,
            "std_prob": p_std,
            "q10_prob": p_q10,
            "q90_prob": p_q90,
            "entropy": h_entropy,
            "margin": margin,
            "consensus_pred": consensus_pred,
            "is_error": is_error,
        })

    # Error discrimination by entropy: Can entropy predict classification error?
    if len(incorrect_entropies) > 0 and len(correct_entropies) > 0:
        entropy_auc = float(roc_auc_score(all_errors, all_entropies))
        # Margin should inversely predict error (lower margin -> higher error)
        margin_auc = float(roc_auc_score(all_errors, [-m for m in all_margins]))
    else:
        entropy_auc = None
        margin_auc = None

    # Uncertainty stratification: Deciles or Quintiles of Entropy
    entropy_bins = np.linspace(0.0, 1.0, 6)
    entropy_stratification: List[Dict[str, Any]] = []

    for b_idx in range(len(entropy_bins) - 1):
        low, high = entropy_bins[b_idx], entropy_bins[b_idx + 1]
        pts_in_bin = [
            r for r in patient_records if low <= r["entropy"] <= high
        ] if b_idx == len(entropy_bins) - 2 else [
            r for r in patient_records if low <= r["entropy"] < high
        ]

        if pts_in_bin:
            bin_y_true = [r["y_true"] for r in pts_in_bin]
            bin_probs = [r["mean_prob"] for r in pts_in_bin]
            bin_errors = [r["is_error"] for r in pts_in_bin]
            bin_sds = [r["std_prob"] for r in pts_in_bin]
            bin_margins = [r["margin"] for r in pts_in_bin]

            bin_brier = float(brier_score_loss(bin_y_true, bin_probs)) if len(pts_in_bin) > 1 else None

            entropy_stratification.append({
                "entropy_bin": f"{low:.1f} - {high:.1f}",
                "patient_count": len(pts_in_bin),
                "error_rate": float(np.mean(bin_errors)),
                "mean_probability": float(np.mean(bin_probs)),
                "mean_variance": float(np.mean(np.square(bin_sds))),
                "mean_margin": float(np.mean(bin_margins)),
                "brier_score": bin_brier,
            })

    # Margin stratification: Distance from threshold
    margin_bins = [0.0, 0.05, 0.10, 0.20, 0.35, 1.0]
    margin_labels = ["< 0.05", "0.05 - 0.10", "0.10 - 0.20", "0.20 - 0.35", ">= 0.35"]
    margin_stratification: List[Dict[str, Any]] = []

    for b_idx in range(len(margin_labels)):
        low, high = margin_bins[b_idx], margin_bins[b_idx + 1]
        pts_in_bin = [
            r for r in patient_records if low <= r["margin"] < high
        ]
        if pts_in_bin:
            bin_errors = [r["is_error"] for r in pts_in_bin]
            bin_sds = [r["std_prob"] for r in pts_in_bin]
            margin_stratification.append({
                "margin_bin": margin_labels[b_idx],
                "patient_count": len(pts_in_bin),
                "error_rate": float(np.mean(bin_errors)),
                "mean_std_prob": float(np.mean(bin_sds)),
            })

    return {
        "n_patients": n_patients,
        "operating_threshold": threshold,
        "overall_error_count": sum(all_errors),
        "overall_error_rate": float(sum(all_errors) / n_patients),
        "empirical_fold_variability": {
            "mean_sd": float(np.mean(all_sds)),
            "std_sd": float(np.std(all_sds)),
            "median_sd": float(np.median(all_sds)),
            "mean_q10_q90_interval_width": float(np.mean(np.array(all_q90) - np.array(all_q10))),
            "methodological_caveat": (
                "Quantiles and standard deviations represent empirical across-model variability "
                "across correlated training partitions, NOT formally calibrated prediction intervals."
            ),
        },
        "entropy_uncertainty": {
            "mean_entropy": float(np.mean(all_entropies)),
            "std_entropy": float(np.std(all_entropies)),
            "median_entropy": float(np.median(all_entropies)),
            "correct_predictions_entropy_mean": float(np.mean(correct_entropies)) if correct_entropies else None,
            "correct_predictions_entropy_median": float(np.median(correct_entropies)) if correct_entropies else None,
            "incorrect_predictions_entropy_mean": float(np.mean(incorrect_entropies)) if incorrect_entropies else None,
            "incorrect_predictions_entropy_median": float(np.median(incorrect_entropies)) if incorrect_entropies else None,
            "entropy_error_auc": entropy_auc,
        },
        "margin_uncertainty": {
            "mean_margin": float(np.mean(all_margins)),
            "median_margin": float(np.median(all_margins)),
            "correct_predictions_margin_mean": float(np.mean(correct_margins)) if correct_margins else None,
            "incorrect_predictions_margin_mean": float(np.mean(incorrect_margins)) if incorrect_margins else None,
            "margin_error_auc": margin_auc,
        },
        "entropy_stratification": entropy_stratification,
        "margin_stratification": margin_stratification,
        "patient_records": patient_records,
    }


def plot_uncertainty_distributions(
    unc_res: Dict[str, Any], target_name: str, output_path: Path
) -> None:
    """Plots entropy distributions for correct vs incorrect predictions and margin vs error rate."""
    setup_plot_style()
    records = unc_res["patient_records"]
    correct_h = [r["entropy"] for r in records if r["is_error"] == 0]
    incorrect_h = [r["entropy"] for r in records if r["is_error"] == 1]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # 1. Entropy Boxplot: Correct vs Incorrect
    data_to_plot = [correct_h, incorrect_h] if incorrect_h else [correct_h]
    labels = ["Correct\n(N={})".format(len(correct_h)), "Error\n(N={})".format(len(incorrect_h))] if incorrect_h else ["Correct"]
    colors = ["#2ca02c", "#d62728"]

    bplot = axes[0].boxplot(data_to_plot, tick_labels=labels, patch_artist=True, widths=0.5)
    for patch, color in zip(bplot["boxes"], colors, strict=False):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    axes[0].set_ylabel("Binary Entropy H(p) [0 = Certain, 1 = Max Uncertainty]", fontsize=10)
    e_auc = unc_res["entropy_uncertainty"]["entropy_error_auc"]
    title_suffix = f" (Error AUC: {e_auc:.3f})" if e_auc is not None else ""
    axes[0].set_title(f"Predictive Entropy vs Classification Accuracy{title_suffix}", fontsize=10, fontweight="bold")
    axes[0].grid(axis="y", alpha=0.5)

    # 2. Margin vs Error Rate Curve
    m_strat = unc_res["margin_stratification"]
    m_labels = [m["margin_bin"] for m in m_strat]
    m_errs = [m["error_rate"] * 100 for m in m_strat]
    m_counts = [m["patient_count"] for m in m_strat]

    bars = axes[1].bar(m_labels, m_errs, color="#e65100", alpha=0.85, edgecolor="#bf360c")
    for bar, count in zip(bars, m_counts, strict=False):
        h = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2.0, h + 1, f"{h:.1f}%\n(N={count})", ha="center", va="bottom", fontsize=8)

    axes[1].set_xlabel("Margin Distance from Decision Threshold |p - threshold|", fontsize=10)
    axes[1].set_ylabel("Empirical Error Rate (%)", fontsize=10)
    axes[1].set_ylim(0, max(m_errs + [10]) * 1.3)
    axes[1].set_title("Empirical Error Rate vs Threshold Proximity", fontsize=10, fontweight="bold")
    axes[1].grid(axis="y", alpha=0.5)

    plt.suptitle(f"{target_name}: Predictive Uncertainty & Error Relationship", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_variance_vs_disagreement(
    unc_res: Dict[str, Any], target_name: str, output_path: Path
) -> None:
    """Plots probability variance vs threshold margin and entropy."""
    setup_plot_style()
    records = unc_res["patient_records"]
    sds = [r["std_prob"] for r in records]
    entropies = [r["entropy"] for r in records]
    errors = [r["is_error"] for r in records]

    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    ax.scatter(
        entropies,
        sds,
        c=["#d62728" if e else "#1f77b4" for e in errors],
        alpha=0.7,
        s=35,
        edgecolors="none",
    )

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", label="Correct Prediction", markerfacecolor="#1f77b4", markersize=7),
        Line2D([0], [0], marker="o", color="w", label="Classification Error", markerfacecolor="#d62728", markersize=7),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=9)
    ax.set_xlabel("Binary Entropy H(p)", fontsize=10)
    ax.set_ylabel("Across-Fold Probability Standard Deviation", fontsize=10)
    ax.set_title(f"{target_name}: Model Instability (SD) vs Predictive Uncertainty (Entropy)", fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.5)

    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def run_experiment_c_for_target(artifacts: TargetCVArtifacts, output_dir: Path) -> Dict[str, Any]:
    """
    Executes Experiment C for a single target:
    - Fold-based empirical predictive variability
    - Binary entropy analysis
    - Margin-based uncertainty
    - Calibration and uncertainty relationship
    - Figures and JSON output
    """
    target = artifacts.target_name
    t_dir = output_dir / target.lower()
    fig_dir = t_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    unc_res = evaluate_uncertainty_metrics(artifacts)

    summary = {
        "target": target,
        "clinical_name": artifacts.clinical_name,
        "model_family": artifacts.model_family,
        "operating_threshold": artifacts.decision_threshold,
        "calibration_method": artifacts.calibration_method or "uncalibrated",
        "scientific_disclaimer": (
            "Empirical fold variability (standard deviation across repeated outer CV folds) "
            "measures model stability, not formally calibrated prediction intervals. "
            "Entropy quantifies predictive uncertainty given model output p, not frequentist epistemic error."
        ),
        "overall_error_count": unc_res["overall_error_count"],
        "overall_error_rate": unc_res["overall_error_rate"],
        "empirical_fold_variability": unc_res["empirical_fold_variability"],
        "entropy_uncertainty": unc_res["entropy_uncertainty"],
        "margin_uncertainty": unc_res["margin_uncertainty"],
        "entropy_stratification": unc_res["entropy_stratification"],
        "margin_stratification": unc_res["margin_stratification"],
    }

    json_path = t_dir / f"{target.lower()}_uncertainty_summary.json"
    save_json(summary, json_path)

    # Save patient-level CSV table
    csv_path = t_dir / f"{target.lower()}_uncertainty_patient_audit.csv"
    pd.DataFrame(unc_res["patient_records"]).to_csv(csv_path, index=False)

    plot_uncertainty_distributions(unc_res, target, fig_dir / "uncertainty_distributions.png")
    plot_variance_vs_disagreement(unc_res, target, fig_dir / "variance_vs_uncertainty.png")

    return summary
