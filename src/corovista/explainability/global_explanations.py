"""
CoroVista - Global Cohort SHAP Explanations & Report Generation
Population-Level Feature Importance Service

Computes population-level global feature importance for each target:
- Mean absolute SHAP values across all 303 cohort patients
- Feature ranking (Top 10 / Top 20)
- Exports machine-readable data/reports/shap_global.json
- Generates publication-quality summary plots in data/reports/shap/
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from src.corovista.explainability.explainers import get_target_explainer
from src.corovista.explainability.feature_mapping import get_human_label
from ml.preprocessing.pipeline import extract_features_and_targets


def compute_global_explanations(
    df_raw: pd.DataFrame,
    output_json_path: Optional[Path] = None,
    plots_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Computes global SHAP importances across all 4 targets for the cohort.

    Parameters:
    -----------
    df_raw: Raw cohort dataframe (Sheet 1 - Table 1).
    output_json_path: Optional path to save shap_global.json.
    plots_dir: Optional path to save diagnostic summary plots.

    Returns:
    --------
    Dict[str, Any]: Structured global explanation summaries for all targets.
    """
    X_raw, _ = extract_features_and_targets(df_raw)
    targets = ["cath", "lad", "lcx", "rca"]
    global_results: Dict[str, Any] = {}

    if plots_dir:
        plots_dir.mkdir(parents=True, exist_ok=True)

    for target in targets:
        explainer = get_target_explainer(target)
        shap_vals, base_val = explainer.explain(X_raw)
        X_trans = explainer.transform_features(X_raw)
        feat_names = explainer.feature_names

        # Mean absolute SHAP value per feature
        mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)

        # Ranked features
        sorted_indices = np.argsort(mean_abs_shap)[::-1]
        ranking = []
        for rank, idx in enumerate(sorted_indices, start=1):
            f_name = feat_names[idx]
            ranking.append({
                "rank": rank,
                "feature": f_name,
                "label": get_human_label(f_name),
                "mean_abs_shap": round(float(mean_abs_shap[idx]), 4),
            })

        global_results[target] = {
            "target": target,
            "clinical_name": {
                "cath": "Overall CAD Status",
                "lad": "Left Anterior Descending Stenosis",
                "lcx": "Left Circumflex Stenosis",
                "rca": "Right Coronary Artery Stenosis",
            }[target],
            "model_family": explainer.model_family,
            "calibration_method": explainer.calibration_method,
            "explanation_space": explainer.explanation_space,
            "calibration_note": (
                "SHAP values explain the underlying predictive model score (log-odds/margin); "
                "probability calibration is applied separately to determine the final visual risk probability."
            ),
            "base_value": round(float(base_val), 4),
            "total_features": len(feat_names),
            "top_10": ranking[:10],
            "top_20": ranking[:20],
            "full_ranking": ranking,
        }

        # Generate summary plot if plots_dir is specified
        if plots_dir:
            fig = plt.figure(figsize=(10, 6))
            # Human labels for plot
            human_cols = [get_human_label(fn) for fn in feat_names]
            shap.summary_plot(
                shap_vals,
                pd.DataFrame(X_trans, columns=human_cols),
                max_display=12,
                show=False,
            )
            plt.title(
                f"SHAP Global Feature Impact — {global_results[target]['clinical_name']}",
                fontsize=12,
                fontweight="bold",
                pad=15,
            )
            plt.xlabel("SHAP Value (Impact on Model Log-Odds Score)", fontsize=10)
            plt.tight_layout()
            plot_file = plots_dir / f"{target}_summary.png"
            plt.savefig(plot_file, dpi=300, bbox_inches="tight")
            plt.close()

    # Save to JSON if path provided
    if output_json_path:
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(global_results, f, indent=2)

    return global_results
