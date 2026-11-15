"""
CoroVista - Experiment A: SHAP Explanation Stability Engine
Evaluates global and patient-level explanation consistency across repeated CV folds.

Research Questions:
1. Do models consistently identify similar top predictive features across training partitions?
2. Are patient-level feature attributions directionally consistent across repeated out-of-fold fits?
3. Does raw-model SHAP reconstruct the uncalibrated model score within numerical tolerance?
"""

import itertools
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from ml.research.cv_protocol import TargetCVArtifacts
from ml.research.utils import (
    compute_pairwise_rank_correlations,
    jaccard_similarity,
    save_json,
    setup_plot_style,
)


def evaluate_global_shap_stability(artifacts: TargetCVArtifacts) -> Dict[str, Any]:
    """
    Computes global feature importance stability across the 25 outer folds:
    - Mean absolute SHAP per feature (mean +- SD across folds)
    - Pairwise Spearman and Kendall rank correlations across fold pairs
    - Top-5 and Top-10 Jaccard overlap across fold pairs
    - Feature selection frequency in top-5 and top-10 lists
    """
    fold_imp_df = artifacts.fold_feature_importances  # shape (25, 57)
    fold_ranks_df = artifacts.fold_feature_ranks  # shape (25, 57), 1 = top
    n_folds = len(fold_imp_df)

    # 1. Feature-level mean importance and rank across folds
    mean_imp = fold_imp_df.mean(axis=0)
    std_imp = fold_imp_df.std(axis=0)
    mean_rank = fold_ranks_df.mean(axis=0)
    std_rank = fold_ranks_df.std(axis=0)

    # 2. Pairwise rank correlations across all fold pairs (300 pairs for 25 folds)
    spearman_corrs: List[float] = []
    kendall_corrs: List[float] = []
    top5_jaccards: List[float] = []
    top10_jaccards: List[float] = []

    fold_indices = list(range(n_folds))
    for f1, f2 in itertools.combinations(fold_indices, 2):
        imp1 = fold_imp_df.iloc[f1].to_numpy()
        imp2 = fold_imp_df.iloc[f2].to_numpy()

        s_rho, k_tau = compute_pairwise_rank_correlations(imp1, imp2)
        if s_rho is not None:
            spearman_corrs.append(s_rho)
        if k_tau is not None:
            kendall_corrs.append(k_tau)

        # Top-5 and Top-10 sets
        top5_f1 = set(fold_ranks_df.iloc[f1].nsmallest(5).index)
        top5_f2 = set(fold_ranks_df.iloc[f2].nsmallest(5).index)
        top5_jaccards.append(jaccard_similarity(top5_f1, top5_f2))

        top10_f1 = set(fold_ranks_df.iloc[f1].nsmallest(10).index)
        top10_f2 = set(fold_ranks_df.iloc[f2].nsmallest(10).index)
        top10_jaccards.append(jaccard_similarity(top10_f1, top10_f2))

    # 3. Selection frequency in top-5 and top-10 lists across the 25 folds
    top5_counts: Dict[str, int] = {feat: 0 for feat in fold_imp_df.columns}
    top10_counts: Dict[str, int] = {feat: 0 for feat in fold_imp_df.columns}

    for f in range(n_folds):
        t5 = fold_ranks_df.iloc[f].nsmallest(5).index
        t10 = fold_ranks_df.iloc[f].nsmallest(10).index
        for feat in t5:
            top5_counts[feat] += 1
        for feat in t10:
            top10_counts[feat] += 1

    top5_freq = {k: v / n_folds for k, v in top5_counts.items() if v > 0}
    top10_freq = {k: v / n_folds for k, v in top10_counts.items() if v > 0}

    # Consolidated feature summary table
    feature_summary = []
    for feat in fold_imp_df.columns:
        feature_summary.append({
            "feature": feat,
            "mean_abs_shap": float(mean_imp[feat]),
            "std_abs_shap": float(std_imp[feat]),
            "mean_rank": float(mean_rank[feat]),
            "std_rank": float(std_rank[feat]),
            "top5_frequency": float(top5_counts[feat] / n_folds),
            "top10_frequency": float(top10_counts[feat] / n_folds),
        })

    feature_summary.sort(key=lambda x: x["mean_rank"])

    return {
        "n_folds": n_folds,
        "n_features": len(fold_imp_df.columns),
        "pairwise_comparisons": len(spearman_corrs),
        "spearman_rank_correlation": {
            "mean": float(np.mean(spearman_corrs)) if spearman_corrs else None,
            "std": float(np.std(spearman_corrs)) if spearman_corrs else None,
            "median": float(np.median(spearman_corrs)) if spearman_corrs else None,
            "q25": float(np.percentile(spearman_corrs, 25)) if spearman_corrs else None,
            "q75": float(np.percentile(spearman_corrs, 75)) if spearman_corrs else None,
            "min": float(np.min(spearman_corrs)) if spearman_corrs else None,
            "max": float(np.max(spearman_corrs)) if spearman_corrs else None,
            "values": spearman_corrs,
        },
        "kendall_rank_correlation": {
            "mean": float(np.mean(kendall_corrs)) if kendall_corrs else None,
            "std": float(np.std(kendall_corrs)) if kendall_corrs else None,
            "median": float(np.median(kendall_corrs)) if kendall_corrs else None,
            "q25": float(np.percentile(kendall_corrs, 25)) if kendall_corrs else None,
            "q75": float(np.percentile(kendall_corrs, 75)) if kendall_corrs else None,
            "min": float(np.min(kendall_corrs)) if kendall_corrs else None,
            "max": float(np.max(kendall_corrs)) if kendall_corrs else None,
            "values": kendall_corrs,
        },
        "top5_jaccard_overlap": {
            "mean": float(np.mean(top5_jaccards)),
            "std": float(np.std(top5_jaccards)),
            "median": float(np.median(top5_jaccards)),
            "min": float(np.min(top5_jaccards)),
            "max": float(np.max(top5_jaccards)),
        },
        "top10_jaccard_overlap": {
            "mean": float(np.mean(top10_jaccards)),
            "std": float(np.std(top10_jaccards)),
            "median": float(np.median(top10_jaccards)),
            "min": float(np.min(top10_jaccards)),
            "max": float(np.max(top10_jaccards)),
        },
        "top5_selection_frequencies": top5_freq,
        "top10_selection_frequencies": top10_freq,
        "feature_summary": feature_summary,
    }


def evaluate_patient_level_shap_stability(artifacts: TargetCVArtifacts) -> Dict[str, Any]:
    """
    Evaluates patient-level explanation stability across repeated CV out-of-fold explanations:
    - Directional consistency (sign agreement of SHAP attributions across repeats)
    - Mean absolute attribution variation (SD across repeats)
    - Per-patient rank correlation across repeat pairs (properly handling undefined zero-variance cases)
    - Per-patient top-5 feature overlap (Jaccard)
    """
    shap_tensor = artifacts.oof_shap_matrix  # shape: (n_patients, n_repeats, n_features)
    n_patients, n_repeats, n_features = shap_tensor.shape
    feature_names = artifacts.feature_names

    # 1. Sign agreement per patient and per feature
    # For each (patient, feature), majority sign count / n_repeats
    sign_agreements_per_patient: List[float] = []
    sign_agreements_per_feature: np.ndarray = np.zeros(n_features)

    # 2. Attribution variation per patient (mean SD across features)
    attribution_sds_per_patient: List[float] = []
    feature_attribution_sds: np.ndarray = np.zeros(n_features)

    # 3. Per-patient pairwise rank correlation across repeats (10 pairs per patient)
    all_patient_spearman_corrs: List[float] = []
    undefined_correlation_count = 0
    total_correlation_pairs = 0

    # 4. Top-5 Jaccard overlap per patient across repeat pairs
    all_patient_top5_jaccards: List[float] = []

    per_patient_stats: List[Dict[str, Any]] = []

    repeat_pairs = list(itertools.combinations(range(n_repeats), 2))

    for pt_idx in range(n_patients):
        pt_shap = shap_tensor[pt_idx]  # shape: (n_repeats, n_features)

        # Skip if any NaN
        if np.isnan(pt_shap).any():
            continue

        # Sign agreement: positive count vs negative count
        pos_counts = np.sum(pt_shap > 0, axis=0)
        neg_counts = np.sum(pt_shap < 0, axis=0)
        maj_counts = np.maximum(pos_counts, neg_counts)
        # Features where all repeats had exactly 0 SHAP count as 100% agreed
        zero_counts = np.sum(pt_shap == 0, axis=0)
        maj_counts = np.maximum(maj_counts, zero_counts)
        pt_feat_agreement = maj_counts / n_repeats
        mean_pt_sign_agreement = float(np.mean(pt_feat_agreement))
        sign_agreements_per_patient.append(mean_pt_sign_agreement)
        sign_agreements_per_feature += pt_feat_agreement

        # Attribution SD across repeats for this patient
        pt_stds = np.std(pt_shap, axis=0)
        mean_pt_sd = float(np.mean(pt_stds))
        attribution_sds_per_patient.append(mean_pt_sd)
        feature_attribution_sds += pt_stds

        # Pairwise correlations and top-5 overlap between repeats
        pt_pair_rhos: List[float] = []
        pt_pair_jaccards: List[float] = []

        for r1, r2 in repeat_pairs:
            total_correlation_pairs += 1
            v1 = pt_shap[r1]
            v2 = pt_shap[r2]

            s_rho, _ = compute_pairwise_rank_correlations(v1, v2)
            if s_rho is not None:
                pt_pair_rhos.append(s_rho)
                all_patient_spearman_corrs.append(s_rho)
            else:
                undefined_correlation_count += 1

            # Top-5 features by absolute attribution
            top5_r1 = set(np.argsort(np.abs(v1))[-5:])
            top5_r2 = set(np.argsort(np.abs(v2))[-5:])
            j_sim = jaccard_similarity(top5_r1, top5_r2)
            pt_pair_jaccards.append(j_sim)
            all_patient_top5_jaccards.append(j_sim)

        per_patient_stats.append({
            "patient_idx": pt_idx,
            "mean_sign_agreement": mean_pt_sign_agreement,
            "mean_attribution_sd": mean_pt_sd,
            "mean_rank_correlation": float(np.mean(pt_pair_rhos)) if pt_pair_rhos else None,
            "mean_top5_jaccard": float(np.mean(pt_pair_jaccards)) if pt_pair_jaccards else None,
        })

    sign_agreements_per_feature /= max(1, n_patients)
    feature_attribution_sds /= max(1, n_patients)

    # Feature-level attribution consistency table
    feature_consistency = []
    for f_idx, feat in enumerate(feature_names):
        feature_consistency.append({
            "feature": feat,
            "mean_sign_agreement": float(sign_agreements_per_feature[f_idx]),
            "mean_attribution_sd": float(feature_attribution_sds[f_idx]),
        })
    feature_consistency.sort(key=lambda x: x["mean_sign_agreement"], reverse=True)

    return {
        "n_patients_evaluated": len(sign_agreements_per_patient),
        "total_correlation_pairs_tested": total_correlation_pairs,
        "undefined_correlation_pairs": undefined_correlation_count,
        "undefined_correlation_rate": float(undefined_correlation_count / max(1, total_correlation_pairs)),
        "sign_agreement": {
            "mean": float(np.mean(sign_agreements_per_patient)),
            "std": float(np.std(sign_agreements_per_patient)),
            "median": float(np.median(sign_agreements_per_patient)),
            "min": float(np.min(sign_agreements_per_patient)),
            "max": float(np.max(sign_agreements_per_patient)),
        },
        "attribution_sd": {
            "mean": float(np.mean(attribution_sds_per_patient)),
            "std": float(np.std(attribution_sds_per_patient)),
            "median": float(np.median(attribution_sds_per_patient)),
            "q90": float(np.percentile(attribution_sds_per_patient, 90)),
        },
        "per_patient_rank_correlation": {
            "mean": float(np.mean(all_patient_spearman_corrs)) if all_patient_spearman_corrs else None,
            "std": float(np.std(all_patient_spearman_corrs)) if all_patient_spearman_corrs else None,
            "median": float(np.median(all_patient_spearman_corrs)) if all_patient_spearman_corrs else None,
            "q25": float(np.percentile(all_patient_spearman_corrs, 25)) if all_patient_spearman_corrs else None,
            "q75": float(np.percentile(all_patient_spearman_corrs, 75)) if all_patient_spearman_corrs else None,
            "min": float(np.min(all_patient_spearman_corrs)) if all_patient_spearman_corrs else None,
            "max": float(np.max(all_patient_spearman_corrs)) if all_patient_spearman_corrs else None,
        },
        "per_patient_top5_jaccard": {
            "mean": float(np.mean(all_patient_top5_jaccards)),
            "std": float(np.std(all_patient_top5_jaccards)),
            "median": float(np.median(all_patient_top5_jaccards)),
            "min": float(np.min(all_patient_top5_jaccards)),
            "max": float(np.max(all_patient_top5_jaccards)),
        },
        "feature_attribution_consistency": feature_consistency,
        "per_patient_stats": per_patient_stats,
    }


def plot_global_shap_importance(
    global_res: Dict[str, Any], target_name: str, output_path: Path, top_n: int = 15
) -> None:
    """Generates bar chart of top N features with fold-level standard deviations."""
    setup_plot_style()
    summary = global_res["feature_summary"][:top_n]
    features = [item["feature"] for item in summary][::-1]
    means = [item["mean_abs_shap"] for item in summary][::-1]
    stds = [item["std_abs_shap"] for item in summary][::-1]

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    y_pos = np.arange(len(features))
    ax.barh(y_pos, means, xerr=stds, align="center", color="#1f77b4", alpha=0.85, capsize=3, edgecolor="#0d47a1")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=9)
    ax.set_xlabel("Mean Absolute SHAP Value (Log-Odds Space)", fontsize=10)
    ax.set_title(f"{target_name}: Top {top_n} Global Feature Importance Across 25 CV Folds", fontsize=11, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_fold_feature_ranks_heatmap(
    artifacts: TargetCVArtifacts, global_res: Dict[str, Any], output_path: Path, top_n: int = 12
) -> None:
    """Generates heatmap showing stability of feature ranks across the 25 outer folds."""
    setup_plot_style()
    top_features = [item["feature"] for item in global_res["feature_summary"][:top_n]]
    ranks_sub = artifacts.fold_feature_ranks[top_features].T  # shape: (top_n, 25)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    cax = ax.imshow(ranks_sub.to_numpy(), aspect="auto", cmap="Blues_r", vmin=1, vmax=25)
    cbar = fig.colorbar(cax, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Feature Rank in Fold (1 = Top Importance)", fontsize=9)

    ax.set_yticks(np.arange(top_n))
    ax.set_yticklabels(top_features, fontsize=9)
    ax.set_xticks(np.arange(0, 25, 5))
    ax.set_xticklabels([f"Fold {i+1}" for i in range(0, 25, 5)], fontsize=9)
    ax.set_xlabel("Outer Cross-Validation Folds (25 Evaluated Folds)", fontsize=10)
    ax.set_title(f"{artifacts.target_name}: Rank Consistency Across 25 CV Folds", fontsize=11, fontweight="bold")

    # Add numeric rank text inside cells
    for i in range(top_n):
        for j in range(25):
            val = int(ranks_sub.iloc[i, j])
            color = "white" if val < 10 else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=6)

    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_correlation_distributions(
    global_res: Dict[str, Any], patient_res: Dict[str, Any], target_name: str, output_path: Path
) -> None:
    """Plots distribution of global fold-to-fold rank correlations and patient-level rank correlations."""
    setup_plot_style()
    global_rhos = global_res["spearman_rank_correlation"]["values"]
    pt_rhos = [p["mean_rank_correlation"] for p in patient_res["per_patient_stats"] if p["mean_rank_correlation"] is not None]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # 1. Global Fold-to-Fold Spearman Corrs
    axes[0].hist(global_rhos, bins=15, color="#2b5c8f", edgecolor="#1a365d", alpha=0.85)
    mean_g = global_res["spearman_rank_correlation"]["mean"]
    axes[0].axvline(mean_g, color="#d9534f", linestyle="--", linewidth=1.5, label=f"Mean: {mean_g:.3f}")
    axes[0].set_xlabel("Spearman Rank Correlation", fontsize=10)
    axes[0].set_ylabel("Fold Pair Frequency", fontsize=10)
    axes[0].set_title("Global Fold-to-Fold Rank Correlation\n(300 Pairwise Fold Comparisons)", fontsize=10, fontweight="bold")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.5)

    # 2. Patient-Level Attribution Rank Corrs
    axes[1].hist(pt_rhos, bins=20, color="#2a9d8f", edgecolor="#1d6f66", alpha=0.85)
    mean_pt = patient_res["per_patient_rank_correlation"]["mean"]
    if mean_pt is not None:
        axes[1].axvline(mean_pt, color="#d9534f", linestyle="--", linewidth=1.5, label=f"Mean: {mean_pt:.3f}")
    axes[1].set_xlabel("Patient Spearman Rank Correlation", fontsize=10)
    axes[1].set_ylabel("Patient Frequency (N=303)", fontsize=10)
    axes[1].set_title("Patient-Level Attribution Consistency\nAcross Repeated Outer Folds", fontsize=10, fontweight="bold")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.5)

    plt.suptitle(f"{target_name}: Explanation Stability Distribution", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def run_experiment_a_for_target(artifacts: TargetCVArtifacts, output_dir: Path) -> Dict[str, Any]:
    """
    Executes Experiment A for a single target:
    - Global SHAP stability
    - Patient-level SHAP stability
    - Numerical reconstruction audit
    - Figure generation
    - JSON results saving
    """
    target = artifacts.target_name
    t_dir = output_dir / target.lower()
    fig_dir = t_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Global stability
    global_res = evaluate_global_shap_stability(artifacts)

    # 2. Patient-level stability
    patient_res = evaluate_patient_level_shap_stability(artifacts)

    # 3. Compile experiment summary
    exp_summary = {
        "target": target,
        "clinical_name": artifacts.clinical_name,
        "model_family": artifacts.model_family,
        "decision_threshold": artifacts.decision_threshold,
        "calibration_method": artifacts.calibration_method or "uncalibrated",
        "explanation_space": "log-odds (model score)",
        "calibration_disclosure": (
            "Raw-model SHAP attributions operate in uncalibrated score space (log-odds / margin). "
            "For calibrated models, SHAP values linearly reconstruct the ensemble mean score, "
            "not the final post-processed calibrated probability."
        ),
        "reconstruction_check": {
            "all_folds_passed": artifacts.reconstruction_all_passed,
            "max_reconstruction_diff": artifacts.max_reconstruction_diff,
            "tolerance": 1e-4,
        },
        "global_stability": global_res,
        "patient_level_stability": patient_res,
    }

    # 4. Save JSON results
    json_path = t_dir / f"{target.lower()}_shap_stability.json"
    save_json(exp_summary, json_path)

    # 5. Export figures
    plot_global_shap_importance(global_res, target, fig_dir / "global_feature_importance.png")
    plot_fold_feature_ranks_heatmap(artifacts, global_res, fig_dir / "fold_feature_ranks_heatmap.png")
    plot_correlation_distributions(global_res, patient_res, target, fig_dir / "correlation_distributions.png")

    return exp_summary
