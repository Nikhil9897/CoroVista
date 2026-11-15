"""
CoroVista - Model Selection Reconciliation & Final Serialization Script
Stage 2: Model Selection Reconciliation

Performs evidence-based model reconciliation across the four targets using
internal repeated stratified CV fold summaries (Mean ± SD across folds;
repeated folds share patients and do not constitute independent datasets or
external validation).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocessing.pipeline import load_dataset
from ml.training.trainer import train_and_save_final_model

DEFAULT_DATASET_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")
DEFAULT_BENCHMARK_PATH = Path("data/reports/reproduction_audit/model_benchmark.json")
FALLBACK_BENCHMARK_PATH = Path("data/reports/model_benchmark.json")


def format_fold_summary(metric_entry: dict, decimals: int = 3) -> str:
    """Formats a repeated-CV fold Mean ± SD summary without assuming fold independence."""
    mean = metric_entry.get("mean")
    std = metric_entry.get("std")
    if mean is None or std is None:
        return "Undefined (N/A)"
    return f"{mean:.{decimals}f} ± {std:.{decimals}f}"


def main(cli_args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="CoroVista Evidence-Based Model Reconciliation")
    parser.add_argument(
        "--benchmark-path",
        type=str,
        default=str(DEFAULT_BENCHMARK_PATH),
        help="Path to benchmark JSON report (defaults to reproduction_audit)",
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default=str(DEFAULT_DATASET_PATH),
        help="Path to raw clinical Excel dataset",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom root directory to serialize models into (defaults to standard models/)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        default=False,
        help="Dry run: print reconciled summary table without serializing models to disk.",
    )
    args = parser.parse_args(cli_args)

    bench_path = Path(args.benchmark_path)
    if not bench_path.exists():
        if FALLBACK_BENCHMARK_PATH.exists():
            print(f"Benchmark report not found at {bench_path}; falling back to {FALLBACK_BENCHMARK_PATH}")
            bench_path = FALLBACK_BENCHMARK_PATH
        else:
            raise FileNotFoundError(f"Benchmark report not found at {bench_path} or {FALLBACK_BENCHMARK_PATH}")

    with open(bench_path, "r", encoding="utf-8") as f:
        bench = json.load(f)

    df = load_dataset(Path(args.dataset_path))

    reconciled_targets = {
        "Cath": {
            "clinical_name": "Overall CAD Status",
            "model_family": "XGBoost",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.50,
            "metrics": bench["Cath"]["calibration_comparison"]["XGBoost_sigmoid"]["standard_threshold_metrics"],
            "standard_metrics": bench["Cath"]["calibration_comparison"]["XGBoost_sigmoid"]["standard_threshold_metrics"],
            "tuned_metrics": bench["Cath"]["calibration_comparison"]["XGBoost_sigmoid"]["tuned_threshold_metrics"],
            "rationale": (
                "XGBoost with Sigmoid Platt calibration achieves lowest Brier score (0.1034) and lowest ECE "
                "(0.1004) with high discrimination (ROC-AUC 0.912 ± 0.040, PR-AUC 0.960 ± 0.020) and 92.1% sensitivity."
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
            "standard_metrics": bench["LAD"]["calibration_comparison"]["XGBoost_sigmoid"]["standard_threshold_metrics"],
            "tuned_metrics": bench["LAD"]["calibration_comparison"]["XGBoost_sigmoid"]["tuned_threshold_metrics"],
            "rationale": (
                "XGBoost with Sigmoid Platt calibration achieves superior probability calibration (Brier 0.1609 vs "
                "0.1674 for RF; ECE 0.1326 vs 0.1486 for RF) and competitive discrimination (PR-AUC 0.882 vs 0.885, "
                "ROC-AUC 0.844 vs 0.853) with 85.7% sensitivity at threshold 0.50."
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
            "standard_metrics": bench["LCX"]["baseline_models"]["XGBoost"]["standard_threshold_metrics"],
            "tuned_metrics": bench["LCX"]["baseline_models"]["XGBoost"]["tuned_threshold_metrics"],
            "rationale": (
                "XGBoost shows modestly higher observed fold-mean discrimination (ROC-AUC 0.736 vs 0.725; "
                "PR-AUC 0.617 vs 0.609) and a slightly lower Brier score (0.2054 vs 0.2098) compared to RandomForest "
                "on repeated-CV fold summaries. These observed differences are small relative to cross-fold variance "
                "(SD ~0.06–0.08) and do not establish formal statistical significance. Standard cutoff 0.50 is retained "
                "as base (F1 0.605, BalAcc 67.4%); inner-OOF tuned threshold 0.35 is available if higher sensitivity "
                "(79.4%) is prioritized."
            ),
        },
        "RCA": {
            "clinical_name": "Right Coronary Artery Stenosis",
            "model_family": "LogisticRegression",
            "vhd_encoding": "onehot",
            "scaler_type": "standard",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.35,
            "metrics": bench["RCA"]["calibration_comparison"]["LogisticRegression_sigmoid"]["tuned_threshold_metrics"],
            "standard_metrics": bench["RCA"]["calibration_comparison"]["LogisticRegression_sigmoid"]["standard_threshold_metrics"],
            "tuned_metrics": bench["RCA"]["calibration_comparison"]["LogisticRegression_sigmoid"]["tuned_threshold_metrics"],
            "rationale": (
                "Logistic Regression with Sigmoid Platt calibration achieves the lowest fold-mean Brier score (0.2060) "
                "and lowest fold-mean ECE (0.1000) with robust discrimination (ROC-AUC 0.716, PR-AUC 0.610). "
                "At standard threshold 0.50, probability compression on this minority class causes sensitivity collapse "
                "(Recall 31.2%, F1 0.403). Operating threshold 0.35 (derived from the sigmoid-calibrated model's "
                "inner-OOF distribution: mean 0.319, range 0.20–0.37; distinct from uncalibrated LR mean 0.303) "
                "resolves probability compression, lifting sensitivity to 79.5% ± 10.7% and F1 to 0.604 ± 0.051."
            ),
        },
    }

    if args.no_save:
        print("\n[DRY RUN] Final model serialization skipped (--no-save enabled). No models written to disk.")
    else:
        # Save finalized pipelines to models/ (or custom output_dir)
        target_dir_map = {"Cath": "cad", "LAD": "lad", "LCX": "lcx", "RCA": "rca"}
        for t_name, cfg in reconciled_targets.items():
            dir_name = target_dir_map.get(t_name, t_name.lower())
            out_path = Path(args.output_dir) / dir_name if args.output_dir else None
            save_dir = train_and_save_final_model(
                target_name=t_name,
                df_raw=df,
                model_config=cfg,
                cv_summary_metrics=cfg["metrics"],
                output_dir=out_path,
                random_state=42,
            )
            print(f"Serialized reconciled model for {t_name} to {save_dir}")

    print("\n=== RECONCILED MODEL SUMMARY TABLE (REPEATED-CV FOLD MEAN ± SD ACROSS 25 FOLDS) ===")
    print(
        f"{'Target':<6} | {'Final Model':<18} | {'Calib Method':<12} | {'Thresh':<8} | "
        f"{'ROC-AUC (Mean±SD)':<18} | {'PR-AUC (Mean±SD)':<18} | "
        f"{'Brier (Mean±SD)':<18} | {'ECE (Mean±SD)':<16} | "
        f"{'F1 @ Thresh':<16} | {'Recall @ Thresh':<18}"
    )
    for t_name, cfg in reconciled_targets.items():
        m = cfg["metrics"]
        roc_s = format_fold_summary(m["roc_auc"])
        pr_s = format_fold_summary(m["pr_auc"])
        brier_s = format_fold_summary(m["brier_score"], decimals=4)
        ece_s = format_fold_summary(m["ece"], decimals=4)
        f1_s = format_fold_summary(m["f1"])
        rec_s = format_fold_summary(m["recall"])
        th_s = f"{cfg['decision_threshold']:.2f}"
        print(
            f"{t_name:<6} | {cfg['model_family']:<18} | {cfg['calibration_method']:<12} | {th_s:<8} | "
            f"{roc_s:<18} | {pr_s:<18} | {brier_s:<18} | {ece_s:<16} | "
            f"{f1_s:<16} | {rec_s:<18}"
        )

    print("\n=== THRESHOLD-SPECIFIC OPERATING METRICS BREAKDOWN (STANDARD 0.50 VS OPERATING/TUNED) ===")
    print(
        f"{'Target':<6} | {'Operating Thresh':<16} | {'Op F1':<16} | {'Op Recall':<16} | {'Op BalAcc':<16} | "
        f"{'Std 0.50 F1':<16} | {'Std 0.50 Recall':<16} | {'Std 0.50 BalAcc':<16}"
    )
    for t_name, cfg in reconciled_targets.items():
        std_m = cfg["standard_metrics"]
        tuned_m = cfg["tuned_metrics"]
        op_thresh = cfg["decision_threshold"]
        op_m = std_m if op_thresh == 0.50 else tuned_m

        op_th_str = f"{op_thresh:.2f}"
        if op_thresh != 0.50:
            op_th_str += " (Tuned)"
        else:
            op_th_str += " (Standard)"

        op_f1 = format_fold_summary(op_m["f1"])
        op_rec = format_fold_summary(op_m["recall"])
        op_bal = format_fold_summary(op_m["balanced_accuracy"])

        std_f1 = format_fold_summary(std_m["f1"])
        std_rec = format_fold_summary(std_m["recall"])
        std_bal = format_fold_summary(std_m["balanced_accuracy"])

        print(
            f"{t_name:<6} | {op_th_str:<16} | {op_f1:<16} | {op_rec:<16} | {op_bal:<16} | "
            f"{std_f1:<16} | {std_rec:<16} | {std_bal:<16}"
        )

    print("\n*Note: All values report repeated-CV fold summaries (Mean ± SD across 25 correlated folds on the 303-patient cohort). "
          "These are internal validation fold summaries, not single aggregate test-set metrics or independent external validation.*")


if __name__ == "__main__":
    main()
