"""
CoroVista - Model Selection Reconciliation & Final Serialization Script
Stage 2: Model Selection Reconciliation

Performs evidence-based model reconciliation across the four targets:
1. Cath: Quantifies XGBoost Sigmoid calibration justification (Brier 0.1018 vs RF 0.1171, F1 0.906 vs 0.902)
2. LCX: Reconciles to XGBoost based on strict empirical superiority (ROC 0.738 vs 0.724, PR 0.622 vs 0.608, Brier 0.204 vs 0.210)
3. RCA: Reconciles to Logistic Regression + Sigmoid calibration (Brier 0.2053, ECE 0.1121) with calibrated threshold 0.38
4. Computes 95% Confidence Intervals for all primary metrics
5. Re-saves final pipelines and metadata in models/cad, lad, lcx, rca
"""

import json
from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from ml.preprocessing.pipeline import load_dataset
from ml.training.trainer import train_and_save_final_model

DATASET_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")
BENCHMARK_PATH = Path("data/reports/model_benchmark.json")

def compute_95_ci(mean: float, std: float, n_runs: int = 25) -> str:
    se = std / np.sqrt(n_runs)
    ci_low = mean - 1.96 * se
    ci_high = mean + 1.96 * se
    return f"[{ci_low:.3f}, {ci_high:.3f}]"

def main():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        bench = json.load(f)

    df = load_dataset(DATASET_PATH)

    reconciled_targets = {
        "Cath": {
            "clinical_name": "Overall CAD Status",
            "model_family": "XGBoost",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.50,
            "metrics": bench["Cath"]["calibration_comparison"]["XGBoost_sigmoid"]["standard_threshold_metrics"],
            "rationale": (
                "XGBoost with Sigmoid Platt calibration achieves lower Brier score (0.1018 vs RF 0.1171, a 13.1% error reduction) "
                "and superior Expected Calibration Error (0.1005). Additionally, calibrated XGBoost attains higher sensitivity (0.920 vs 0.901) "
                "and higher F1-score (0.906 vs 0.902) than Random Forest, with overlapping 95% CIs on ROC-AUC [0.899, 0.931] vs [0.906, 0.935]."
            )
        },
        "LAD": {
            "clinical_name": "Left Anterior Descending Stenosis",
            "model_family": "XGBoost",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.50,
            "metrics": bench["LAD"]["calibration_comparison"]["XGBoost_sigmoid"]["standard_threshold_metrics"],
            "rationale": (
                "XGBoost with Sigmoid Platt calibration delivers superior probability calibration (Brier 0.1600 vs RF 0.1674; ECE 0.1170) "
                "while maintaining high cross-validated discrimination within this dataset (ROC-AUC 0.842, PR-AUC 0.880, Recall 0.850)."
            )
        },
        "LCX": {
            "clinical_name": "Left Circumflex Stenosis",
            "model_family": "XGBoost",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "uncalibrated",
            "decision_threshold": 0.50,
            "metrics": bench["LCX"]["baseline_models"]["XGBoost"]["standard_threshold_metrics"],
            "rationale": (
                "Reconciled from Random Forest to XGBoost based on strict empirical superiority across all evaluation dimensions: "
                "higher ROC-AUC (0.738 vs 0.724), higher PR-AUC (0.622 vs 0.608), higher F1 (0.606 vs 0.585), higher recall (0.611 vs 0.576), "
                "and lower Brier calibration error (0.2041 vs 0.2099)."
            )
        },
        "RCA": {
            "clinical_name": "Right Coronary Artery Stenosis",
            "model_family": "LogisticRegression",
            "vhd_encoding": "onehot",
            "scaler_type": "standard",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.38,
            "metrics": bench["RCA"]["calibration_comparison"]["LogisticRegression_sigmoid"]["standard_threshold_metrics"],
            "rationale": (
                "Logistic Regression with Sigmoid Platt calibration achieves the lowest Brier score (0.2053) and lowest ECE (0.1121) across all RCA models. "
                "With the decision threshold calibrated to 0.38 (aligning with the 37.6% class prevalence), it maintains high sensitivity (Recall 0.652, F1 0.595) "
                "while providing linear log-odds stability on this smaller vascular territory."
            )
        }
    }

    # Save finalized pipelines to models/
    for t_name, cfg in reconciled_targets.items():
        save_dir = train_and_save_final_model(
            target_name=t_name,
            df_raw=df,
            model_config=cfg,
            cv_summary_metrics=cfg["metrics"],
            random_state=42
        )
        print(f"Serialized reconciled model for {t_name} to {save_dir}")

    print("\n=== RECONCILED MODEL SUMMARY TABLE ===")
    print(f"{'Target':<6} | {'Final Model':<18} | {'Calib':<12} | {'ROC-AUC (95% CI)':<22} | {'PR-AUC (95% CI)':<22} | {'F1 (95% CI)':<22} | {'Brier (95% CI)':<22}")
    for t_name, cfg in reconciled_targets.items():
        m = cfg["metrics"]
        roc_ci = f"{m['roc_auc']['mean']:.3f} {compute_95_ci(m['roc_auc']['mean'], m['roc_auc']['std'])}"
        pr_ci = f"{m['pr_auc']['mean']:.3f} {compute_95_ci(m['pr_auc']['mean'], m['pr_auc']['std'])}"
        f1_ci = f"{m['f1']['mean']:.3f} {compute_95_ci(m['f1']['mean'], m['f1']['std'])}"
        brier_ci = f"{m['brier_score']['mean']:.3f} {compute_95_ci(m['brier_score']['mean'], m['brier_score']['std'])}"
        print(f"{t_name:<6} | {cfg['model_family']:<18} | {cfg['calibration_method']:<12} | {roc_ci:<22} | {pr_ci:<22} | {f1_ci:<22} | {brier_ci:<22}")

if __name__ == "__main__":
    main()
