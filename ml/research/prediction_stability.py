"""
CoroVista - Experiment B: Prediction Stability Engine
Evaluates individual patient prediction stability and classification agreement
across repeated training partitions.

Research Questions:
1. Do individual patient predicted probabilities remain stable across independently trained folds?
2. How frequently do discrete classification decisions flip near operating thresholds?
3. Are patient relative risk rankings preserved across repeated cross-validation splits?
"""

import itertools
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from ml.research.cv_protocol import TargetCVArtifacts
from ml.research.utils import jaccard_similarity, save_json, setup_plot_style


def evaluate_probability_and_classification_stability(
    artifacts: TargetCVArtifacts,
) -> Dict[str, Any]:
    """
    Evaluates per-patient probability stability and classification agreement across 5 repeats:
    - Per-patient mean, SD, IQR, range, CV
    - Classification agreement (5/5, 4/5, 3/5)
    - Label flip frequency and near-threshold sensitivity
    - Anonymized high-instability patient list
    """
    df_oof = artifacts.oof_predictions_df
    threshold = artifacts.decision_threshold
    patients = sorted(df_oof["patient_idx"].unique())
    n_patients = len(patients)

    patient_records: List[Dict[str, Any]] = []

    prob_sds: List[float] = []
    prob_iqrs: List[float] = []
    prob_ranges: List[float] = []
    prob_cvs: List[float] = []  # Computed only for mean >= 0.05
    agreements: List[float] = []
    flip_counts: List[int] = []
    distances_to_threshold: List[float] = []

    high_instability_patients: List[Dict[str, Any]] = []

    for pt in patients:
        sub = df_oof[df_oof["patient_idx"] == pt].sort_values("repeat_idx")
        probs = sub["prob"].to_numpy()
        preds = sub["pred"].to_numpy()
        y_true = int(sub["y_true"].iloc[0])

        p_mean = float(np.mean(probs))
        p_std = float(np.std(probs))
        p_iqr = float(np.percentile(probs, 75) - np.percentile(probs, 25))
        p_min = float(np.min(probs))
        p_max = float(np.max(probs))
        p_range = float(p_max - p_min)

        # CV only when p_mean >= 0.05 to avoid division by zero or near-zero inflation
        if p_mean >= 0.05:
            p_cv = float(p_std / p_mean)
            prob_cvs.append(p_cv)
        else:
            p_cv = None

        # Classification agreement
        n_pos = int(np.sum(preds == 1))
        n_neg = int(np.sum(preds == 0))
        n_total = len(preds)
        agreement = float(max(n_pos, n_neg) / n_total)
        is_consistent = agreement == 1.0

        # Number of pairwise disagreements across repeats (out of 10 pairs)
        disagreements = 0
        pair_count = 0
        for r1, r2 in itertools.combinations(range(len(preds)), 2):
            pair_count += 1
            if preds[r1] != preds[r2]:
                disagreements += 1

        dist_to_thresh = float(abs(p_mean - threshold))

        prob_sds.append(p_std)
        prob_iqrs.append(p_iqr)
        prob_ranges.append(p_range)
        agreements.append(agreement)
        flip_counts.append(disagreements)
        distances_to_threshold.append(dist_to_thresh)

        rec = {
            "patient_idx": int(pt),
            "y_true": y_true,
            "mean_prob": p_mean,
            "std_prob": p_std,
            "iqr_prob": p_iqr,
            "min_prob": p_min,
            "max_prob": p_max,
            "range_prob": p_range,
            "cv_prob": p_cv,
            "agreement": agreement,
            "disagreement_pairs": disagreements,
            "is_consistent": is_consistent,
            "distance_to_threshold": dist_to_thresh,
        }
        patient_records.append(rec)

        # Flag high-instability patients (agreement <= 0.60 or SD > 0.15)
        if agreement <= 0.60 or p_std > 0.15:
            high_instability_patients.append({
                "patient_idx": int(pt),
                "y_true": y_true,
                "mean_prob": p_mean,
                "std_prob": p_std,
                "agreement": agreement,
                "disagreement_pairs": disagreements,
                "probs_per_repeat": [float(p) for p in probs],
            })

    # Cohort summary
    n_consistent = sum(1 for a in agreements if a == 1.0)
    pct_consistent = float(n_consistent / n_patients)
    n_80_pct = sum(1 for a in agreements if a >= 0.80)
    pct_80 = float(n_80_pct / n_patients)

    # Near-threshold breakdown: distance bins
    dist_bins = [0.0, 0.05, 0.10, 0.20, 1.0]
    bin_labels = ["< 0.05", "0.05 - 0.10", "0.10 - 0.20", ">= 0.20"]
    threshold_stratification = []

    for b_idx in range(len(bin_labels)):
        low, high = dist_bins[b_idx], dist_bins[b_idx + 1]
        pts_in_bin = [
            r for r in patient_records if low <= r["distance_to_threshold"] < high
        ]
        if pts_in_bin:
            bin_agreements = [r["agreement"] for r in pts_in_bin]
            bin_sds = [r["std_prob"] for r in pts_in_bin]
            bin_flips = [r["disagreement_pairs"] for r in pts_in_bin]
            threshold_stratification.append({
                "bin": bin_labels[b_idx],
                "count": len(pts_in_bin),
                "mean_agreement": float(np.mean(bin_agreements)),
                "perfect_agreement_pct": float(
                    sum(1 for a in bin_agreements if a == 1.0) / len(pts_in_bin)
                ),
                "mean_std_prob": float(np.mean(bin_sds)),
                "mean_disagreement_pairs": float(np.mean(bin_flips)),
            })

    return {
        "n_patients": n_patients,
        "operating_threshold": threshold,
        "probability_stability": {
            "mean_sd": float(np.mean(prob_sds)),
            "std_sd": float(np.std(prob_sds)),
            "median_sd": float(np.median(prob_sds)),
            "q90_sd": float(np.percentile(prob_sds, 90)),
            "max_sd": float(np.max(prob_sds)),
            "pct_sd_over_0_05": float(sum(1 for s in prob_sds if s > 0.05) / n_patients),
            "pct_sd_over_0_10": float(sum(1 for s in prob_sds if s > 0.10) / n_patients),
            "mean_iqr": float(np.mean(prob_iqrs)),
            "median_iqr": float(np.median(prob_iqrs)),
            "mean_range": float(np.mean(prob_ranges)),
            "median_range": float(np.median(prob_ranges)),
            "cv_summary": {
                "evaluated_patients_count": len(prob_cvs),
                "min_mean_prob_filter": 0.05,
                "mean_cv": float(np.mean(prob_cvs)) if prob_cvs else None,
                "median_cv": float(np.median(prob_cvs)) if prob_cvs else None,
            },
        },
        "classification_stability": {
            "mean_agreement": float(np.mean(agreements)),
            "pct_100_percent_consistent": pct_consistent,
            "pct_at_least_80_percent_consistent": pct_80,
            "mean_disagreement_pairs": float(np.mean(flip_counts)),
            "max_disagreement_pairs": int(np.max(flip_counts)),
            "threshold_proximity_stratification": threshold_stratification,
            "high_instability_patients_count": len(high_instability_patients),
            "high_instability_patients": high_instability_patients,
        },
        "patient_records": patient_records,
    }


def evaluate_risk_ranking_stability(artifacts: TargetCVArtifacts) -> Dict[str, Any]:
    """
    Evaluates patient risk ranking stability across the 5 cross-validation repeats:
    - Pairwise Spearman correlation of risk vectors between repeat pairs (10 pairs)
    - Top-10% and Top-20% high-risk patient overlap (Jaccard similarity)
    - Per-patient risk rank standard deviation across repeats
    """
    df_oof = artifacts.oof_predictions_df
    repeats = sorted(df_oof["repeat_idx"].unique())
    n_repeats = len(repeats)
    n_patients = len(df_oof["patient_idx"].unique())

    # Build matrix of predicted probabilities: shape (n_patients, n_repeats)
    prob_matrix = np.zeros((n_patients, n_repeats), dtype=float)
    rank_matrix = np.zeros((n_patients, n_repeats), dtype=float)

    for r_idx in repeats:
        sub = df_oof[df_oof["repeat_idx"] == r_idx].sort_values("patient_idx")
        p_vec = sub["prob"].to_numpy()
        prob_matrix[:, r_idx] = p_vec
        # Rank descending: 1 = highest risk
        rank_matrix[:, r_idx] = stats.rankdata(-p_vec, method="average")

    spearman_rhos: List[float] = []
    top10_pct_jaccards: List[float] = []
    top20_pct_jaccards: List[float] = []

    k10 = max(1, int(round(0.10 * n_patients)))
    k20 = max(1, int(round(0.20 * n_patients)))

    for r1, r2 in itertools.combinations(repeats, 2):
        s_rho, _ = stats.spearmanr(prob_matrix[:, r1], prob_matrix[:, r2])
        spearman_rhos.append(float(s_rho))

        top10_r1 = set(np.argsort(-prob_matrix[:, r1])[:k10])
        top10_r2 = set(np.argsort(-prob_matrix[:, r2])[:k10])
        top10_pct_jaccards.append(jaccard_similarity(top10_r1, top10_r2))

        top20_r1 = set(np.argsort(-prob_matrix[:, r1])[:k20])
        top20_r2 = set(np.argsort(-prob_matrix[:, r2])[:k20])
        top20_pct_jaccards.append(jaccard_similarity(top20_r1, top20_r2))

    # Per-patient rank standard deviation across repeats
    patient_rank_sds = np.std(rank_matrix, axis=1)

    return {
        "n_repeats": n_repeats,
        "n_patients": n_patients,
        "spearman_rank_correlation": {
            "mean": float(np.mean(spearman_rhos)),
            "std": float(np.std(spearman_rhos)),
            "median": float(np.median(spearman_rhos)),
            "min": float(np.min(spearman_rhos)),
            "max": float(np.max(spearman_rhos)),
            "values": spearman_rhos,
        },
        "top10_pct_overlap": {
            "k_patients": k10,
            "mean_jaccard": float(np.mean(top10_pct_jaccards)),
            "std_jaccard": float(np.std(top10_pct_jaccards)),
            "min_jaccard": float(np.min(top10_pct_jaccards)),
            "max_jaccard": float(np.max(top10_pct_jaccards)),
        },
        "top20_pct_overlap": {
            "k_patients": k20,
            "mean_jaccard": float(np.mean(top20_pct_jaccards)),
            "std_jaccard": float(np.std(top20_pct_jaccards)),
            "min_jaccard": float(np.min(top20_pct_jaccards)),
            "max_jaccard": float(np.max(top20_pct_jaccards)),
        },
        "patient_rank_sd": {
            "mean": float(np.mean(patient_rank_sds)),
            "median": float(np.median(patient_rank_sds)),
            "q90": float(np.percentile(patient_rank_sds, 90)),
            "max": float(np.max(patient_rank_sds)),
        },
    }


def plot_prediction_stability_distributions(
    pred_res: Dict[str, Any], target_name: str, output_path: Path
) -> None:
    """Generates distribution plots for probability SD and classification agreement."""
    setup_plot_style()
    records = pred_res["patient_records"]
    sds = [r["std_prob"] for r in records]
    agreements = [r["agreement"] for r in records]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # 1. Probability SD Histogram
    axes[0].hist(sds, bins=20, color="#1f77b4", edgecolor="#0d47a1", alpha=0.85)
    mean_sd = pred_res["probability_stability"]["mean_sd"]
    axes[0].axvline(mean_sd, color="#d9534f", linestyle="--", linewidth=1.5, label=f"Mean: {mean_sd:.3f}")
    axes[0].set_xlabel("Probability Standard Deviation Across Repeats", fontsize=10)
    axes[0].set_ylabel("Patient Count (N=303)", fontsize=10)
    axes[0].set_title("Out-of-Fold Probability Variability", fontsize=10, fontweight="bold")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.5)

    # 2. Classification Agreement Bar Chart
    agr_counts = {1.0: 0, 0.8: 0, 0.6: 0}
    for a in agreements:
        k = round(a, 1)
        if k in agr_counts:
            agr_counts[k] += 1
    bars = axes[1].bar(["100% (5/5)", "80% (4/5)", "60% (3/5)"], [agr_counts[1.0], agr_counts[0.8], agr_counts[0.6]],
                      color=["#2ca02c", "#ff7f0e", "#d62728"], alpha=0.85, edgecolor="#333333")
    for bar in bars:
        h = bar.get_height()
        pct = (h / len(records)) * 100
        axes[1].text(bar.get_x() + bar.get_width()/2., h + 2, f"{h} ({pct:.1f}%)", ha="center", va="bottom", fontsize=9)
    axes[1].set_ylabel("Patient Count", fontsize=10)
    axes[1].set_ylim(0, max(agr_counts.values()) * 1.15)
    axes[1].set_title("Discrete Classification Agreement", fontsize=10, fontweight="bold")
    axes[1].grid(axis="y", alpha=0.5)

    plt.suptitle(f"{target_name}: Prediction & Classification Stability", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_threshold_sensitivity_and_ranking(
    pred_res: Dict[str, Any], rank_res: Dict[str, Any], target_name: str, output_path: Path
) -> None:
    """Generates scatter plot of distance to threshold vs flip frequency, and ranking correlations."""
    setup_plot_style()
    records = pred_res["patient_records"]
    dists = [r["distance_to_threshold"] for r in records]
    flips = [r["disagreement_pairs"] for r in records]
    threshold = pred_res["operating_threshold"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # 1. Distance to threshold vs Disagreements
    axes[0].scatter(dists, flips, alpha=0.6, color="#e65100", edgecolors="none", s=28)
    axes[0].set_xlabel(f"Absolute Distance from Threshold |p - {threshold:.2f}|", fontsize=10)
    axes[0].set_ylabel("Pairwise Disagreement Count (Max 10)", fontsize=10)
    axes[0].set_title("Classification Instability Near Threshold", fontsize=10, fontweight="bold")
    axes[0].grid(True, alpha=0.5)

    # 2. Risk Ranking Correlation Histogram
    rhos = rank_res["spearman_rank_correlation"]["values"]
    axes[1].hist(rhos, bins=8, color="#5e35b1", edgecolor="#311b92", alpha=0.85)
    mean_rho = rank_res["spearman_rank_correlation"]["mean"]
    axes[1].axvline(mean_rho, color="#d9534f", linestyle="--", linewidth=1.5, label=f"Mean: {mean_rho:.3f}")
    axes[1].set_xlabel("Spearman Rank Correlation Across Repeat Pairs", fontsize=10)
    axes[1].set_ylabel("Repeat Pair Frequency (10 Pairs)", fontsize=10)
    axes[1].set_title("Patient Risk Ranking Stability", fontsize=10, fontweight="bold")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.5)

    plt.suptitle(f"{target_name}: Threshold Sensitivity & Ranking Invariance", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def run_experiment_b_for_target(artifacts: TargetCVArtifacts, output_dir: Path) -> Dict[str, Any]:
    """
    Executes Experiment B for a single target:
    - Probability variability metrics
    - Classification stability and threshold sensitivity
    - Risk ranking stability
    - Figure generation
    - JSON results saving
    """
    target = artifacts.target_name
    t_dir = output_dir / target.lower()
    fig_dir = t_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    prob_res = evaluate_probability_and_classification_stability(artifacts)
    rank_res = evaluate_risk_ranking_stability(artifacts)

    summary = {
        "target": target,
        "clinical_name": artifacts.clinical_name,
        "model_family": artifacts.model_family,
        "operating_threshold": artifacts.decision_threshold,
        "calibration_method": artifacts.calibration_method or "uncalibrated",
        "probability_stability": prob_res["probability_stability"],
        "classification_stability": prob_res["classification_stability"],
        "risk_ranking_stability": rank_res,
    }

    json_path = t_dir / f"{target.lower()}_prediction_stability.json"
    save_json(summary, json_path)

    # Export patient-level CSV table for auditability
    csv_path = t_dir / f"{target.lower()}_patient_stability_audit.csv"
    pd.DataFrame(prob_res["patient_records"]).to_csv(csv_path, index=False)

    plot_prediction_stability_distributions(prob_res, target, fig_dir / "prediction_stability_distributions.png")
    plot_threshold_sensitivity_and_ranking(prob_res, rank_res, target, fig_dir / "threshold_sensitivity_and_ranking.png")

    return summary
