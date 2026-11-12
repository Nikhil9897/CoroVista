"""
CoroVista - Model Selection Reconciliation & Final Serialization Script
Stage 2: Model Selection Reconciliation

Performs evidence-based model reconciliation across the four targets using
internal repeated stratified CV fold summaries (Mean ± SD across folds;
repeated folds share patients and do not constitute independent datasets or
external validation).
"""

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocessing.pipeline import load_dataset
from ml.training.trainer import train_and_save_final_model

DATASET_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")
BENCHMARK_PATH = Path("data/reports/model_benchmark.json")


def format_fold_summary(metric_entry: dict, decimals: int = 3) -> str:
    """Formats a repeated-CV fold Mean ± SD summary without assuming fold independence."""
    mean = metric_entry.get("mean")
    std = metric_entry.get("std")
    if mean is None or std is None:
        return "Undefined (N/A)"
    return f"{mean:.{decimals}f} ± {std:.{decimals}f}"


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
                "XGBoost with Sigmoid Platt calibration reduces Brier score and Expected Calibration Error "
                "compared to uncalibrated baselines on internal repeated CV."
            ),
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
                "XGBoost with Sigmoid Platt calibration improves probability calibration while maintaining "
                "strong internal repeated-CV discrimination."
            ),
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
                "XGBoost selected based on internal repeated-CV fold discrimination and Brier score."
            ),
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
                "Logistic Regression with Sigmoid calibration achieves balanced calibration error and "
                "linear log-odds stability on internal repeated CV."
            ),
        },
    }

    # Save finalized pipelines to models/
    for t_name, cfg in reconciled_targets.items():
        save_dir = train_and_save_final_model(
            target_name=t_name,
            df_raw=df,
            model_config=cfg,
            cv_summary_metrics=cfg["metrics"],
            random_state=42,
        )
        print(f"Serialized reconciled model for {t_name} to {save_dir}")

    print("\n=== RECONCILED MODEL SUMMARY TABLE (INTERNAL REPEATED-CV FOLD MEAN ± SD) ===")
    print(f"{'Target':<6} | {'Final Model':<18} | {'Calib':<12} | {'ROC-AUC (Fold Mean±SD)':<22} | {'PR-AUC (Fold Mean±SD)':<22} | {'F1 (Fold Mean±SD)':<22} | {'Brier (Fold Mean±SD)':<22}")
    for t_name, cfg in reconciled_targets.items():
        m = cfg["metrics"]
        roc_s = format_fold_summary(m["roc_auc"])
        pr_s = format_fold_summary(m["pr_auc"])
        f1_s = format_fold_summary(m["f1"])
        brier_s = format_fold_summary(m["brier_score"], decimals=4)
        print(f"{t_name:<6} | {cfg['model_family']:<18} | {cfg['calibration_method']:<12} | {roc_s:<22} | {pr_s:<22} | {f1_s:<22} | {brier_s:<22}")
    print("\nNote: Repeated-CV fold summaries share the 303-patient cohort and are not independent external validation.")


if __name__ == "__main__":
    main()
