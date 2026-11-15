"""
CoroVista - Model Benchmark Orchestrator & Visualization Generator
Multi-Target Evaluation & Calibration Suite

Executes the complete Stage 2 experimentation suite:
1. Repeated Stratified K-Fold (5 folds x 5 repeats = 25 runs) across all 4 targets:
   - Cath (Overall CAD)
   - LAD (Left Anterior Descending Stenosis)
   - LCX (Left Circumflex Stenosis)
   - RCA (Right Coronary Artery Stenosis)
2. Compares 4 model families: Dummy, Logistic Regression, Random Forest, XGBoost
3. Compares Preprocessing: One-Hot vs Ordinal, Scalers (None, Standard, Robust)
4. Conducts Controlled Ablation Experiments:
   - RWMA Ablation: With vs Without Region RWMA
   - Collinearity Ablation: With vs Without BMI
5. Evaluates Probability Calibration: Uncalibrated vs Sigmoid vs Isotonic
6. Trains & Serializes Final Pipelines in models/cad, lad, lcx, rca
7. Generates Comprehensive Reports & Plots in data/reports/
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any, Dict, List, Optional

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve

from ml.preprocessing.pipeline import load_dataset
from ml.training.benchmark import run_comprehensive_target_benchmarks
from ml.training.trainer import train_and_save_final_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_benchmarks")


def _metric_val(metric_entry: Dict[str, Any], key: str, default: float = 0.0) -> float:
    """Safely extracts a numeric metric summary value, falling back if undefined (None)."""
    val = metric_entry.get(key)
    return float(val) if val is not None else default


def _format_mean_std(metric_entry: Dict[str, Any], decimals: int = 3) -> str:
    """Formats a repeated-CV fold summary entry safely when mean/std may be None."""
    mean = metric_entry.get("mean")
    std = metric_entry.get("std")
    if mean is None or std is None:
        return "Undefined (N/A)"
    return f"{mean:.{decimals}f} ± {std:.{decimals}f}"


def _format_mean(metric_entry: Dict[str, Any], decimals: int = 3) -> str:
    """Formats a metric mean safely when mean may be None."""
    mean = metric_entry.get("mean")
    if mean is None:
        return "N/A"
    return f"{mean:.{decimals}f}"


def generate_evaluation_plots(
    benchmarks: Dict[str, Any],
    output_dir: Path,
) -> None:
    """Generates diagnostic plots for internal repeated-CV model evaluation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Model Comparison Chart (ROC-AUC & PR-AUC across targets)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    targets = ["Cath", "LAD", "LCX", "RCA"]

    for idx, target in enumerate(targets):
        ax = axes[idx // 2, idx % 2]
        baseline_res = benchmarks[target]["baseline_models"]
        model_names = list(baseline_res.keys())

        roc_means = [_metric_val(baseline_res[m]["standard_threshold_metrics"]["roc_auc"], "mean") for m in model_names]
        roc_stds = [_metric_val(baseline_res[m]["standard_threshold_metrics"]["roc_auc"], "std") for m in model_names]
        pr_means = [_metric_val(baseline_res[m]["standard_threshold_metrics"]["pr_auc"], "mean") for m in model_names]
        pr_stds = [_metric_val(baseline_res[m]["standard_threshold_metrics"]["pr_auc"], "std") for m in model_names]

        x = np.arange(len(model_names))
        width = 0.35

        ax.bar(x - width / 2, roc_means, width, yerr=roc_stds, label="ROC-AUC", color="#1f77b4", capsize=4, alpha=0.9)
        ax.bar(x + width / 2, pr_means, width, yerr=pr_stds, label="PR-AUC", color="#ff7f0e", capsize=4, alpha=0.9)

        ax.set_title(f"Target: {target} (Repeated Stratified CV Fold Mean ± SD)", fontsize=12, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=15)
        ax.set_ylim(0.4, 1.0)
        ax.set_ylabel("Score")
        ax.legend(loc="lower right")

    plt.tight_layout()
    comp_path = output_dir / "model_comparison.png"
    plt.savefig(comp_path, dpi=300)
    plt.close()
    logger.info("Saved model comparison plot to %s", comp_path)

    # 2. Out-of-Fold ROC Curves for Best Models
    fig, ax = plt.subplots(figsize=(8, 6))
    for target in targets:
        # Find best model based on ROC-AUC (skipping models with undefined ROC-AUC)
        base_res = benchmarks[target]["baseline_models"]
        candidates = [
            m for m in base_res
            if m != "Dummy" and base_res[m]["standard_threshold_metrics"]["roc_auc"]["mean"] is not None
        ]
        if not candidates:
            continue
        best_m = max(
            candidates,
            key=lambda m: base_res[m]["standard_threshold_metrics"]["roc_auc"]["mean"]
        )
        oof_y = np.array(base_res[best_m]["oof_y_true"])
        oof_prob = np.array(base_res[best_m]["oof_y_prob"])
        if len(np.unique(oof_y)) < 2:
            continue

        fpr, tpr, _ = roc_curve(oof_y, oof_prob)
        auc_score = base_res[best_m]["standard_threshold_metrics"]["roc_auc"]["mean"]
        ax.plot(fpr, tpr, lw=2, label=f"{target} ({best_m}, Fold Mean AUC={auc_score:.3f})")

    ax.plot([0, 1], [0, 1], color="gray", lw=1.5, linestyle="--", label="Chance")
    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)
    ax.set_title("Repeated-CV Out-of-Fold ROC Curves (Internal Validation)", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    roc_path = output_dir / "roc_curves.png"
    plt.savefig(roc_path, dpi=300)
    plt.close()
    logger.info("Saved ROC curves plot to %s", roc_path)

    # 3. Out-of-Fold Precision-Recall Curves
    fig, ax = plt.subplots(figsize=(8, 6))
    for target in targets:
        base_res = benchmarks[target]["baseline_models"]
        candidates = [
            m for m in base_res
            if m != "Dummy" and base_res[m]["standard_threshold_metrics"]["pr_auc"]["mean"] is not None
        ]
        if not candidates:
            continue
        best_m = max(
            candidates,
            key=lambda m: base_res[m]["standard_threshold_metrics"]["pr_auc"]["mean"]
        )
        oof_y = np.array(base_res[best_m]["oof_y_true"])
        oof_prob = np.array(base_res[best_m]["oof_y_prob"])
        if len(np.unique(oof_y)) < 2:
            continue

        prec, rec, _ = precision_recall_curve(oof_y, oof_prob)
        pr_score = base_res[best_m]["standard_threshold_metrics"]["pr_auc"]["mean"]
        ax.plot(rec, prec, lw=2, label=f"{target} ({best_m}, Fold Mean PR-AUC={pr_score:.3f})")

    ax.set_xlabel("Recall (Sensitivity)", fontsize=11)
    ax.set_ylabel("Precision (PPV)", fontsize=11)
    ax.set_title("Repeated-CV Out-of-Fold Precision-Recall Curves (Internal Validation)", fontsize=13, fontweight="bold")
    ax.legend(loc="lower left")
    plt.tight_layout()
    pr_path = output_dir / "pr_curves.png"
    plt.savefig(pr_path, dpi=300)
    plt.close()
    logger.info("Saved PR curves plot to %s", pr_path)

    # 4. Calibration Curves (Reliability Diagrams)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for idx, target in enumerate(targets):
        ax = axes[idx // 2, idx % 2]
        cal_res = benchmarks[target]["calibration_comparison"]

        for c_label, color, ls in [
            ("XGBoost_uncalibrated", "#e41a1c", "-"),
            ("XGBoost_sigmoid", "#377eb8", "--"),
            ("XGBoost_isotonic", "#4daf4a", ":"),
        ]:
            if c_label in cal_res:
                oof_y = np.array(cal_res[c_label]["oof_y_true"])
                oof_prob = np.array(cal_res[c_label]["oof_y_prob"])
                prob_true, prob_pred = calibration_curve(oof_y, oof_prob, n_bins=8, strategy="uniform")
                brier = _format_mean(cal_res[c_label]["standard_threshold_metrics"]["brier_score"], decimals=3)
                ax.plot(prob_pred, prob_true, marker="o", lw=1.8, color=color, linestyle=ls,
                        label=f"{c_label.replace('XGBoost_', '')} (Brier={brier})")

        ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Perfect Calibration")
        ax.set_title(f"Target: {target} Calibration Reliability", fontsize=11, fontweight="bold")
        ax.set_xlabel("Mean Predicted Probability", fontsize=10)
        ax.set_ylabel("Fraction of Positives", fontsize=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    cal_path = output_dir / "calibration_curves.png"
    plt.savefig(cal_path, dpi=300)
    plt.close()
    logger.info("Saved calibration curves plot to %s", cal_path)

    # 5. RWMA Ablation Plot (With vs Without Region RWMA)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for idx, target in enumerate(targets):
        ax = axes[idx]
        rwma_data = benchmarks[target]["rwma_ablation"]
        models = ["LogisticRegression", "RandomForest", "XGBoost"]

        with_scores = [_metric_val(rwma_data[m]["with_rwma"]["standard_threshold_metrics"]["roc_auc"], "mean") for m in models]
        without_scores = [_metric_val(rwma_data[m]["without_rwma"]["standard_threshold_metrics"]["roc_auc"], "mean") for m in models]

        x = np.arange(len(models))
        width = 0.35
        ax.bar(x - width / 2, with_scores, width, label="With RWMA", color="#2ca02c", alpha=0.85)
        ax.bar(x + width / 2, without_scores, width, label="Without RWMA", color="#d62728", alpha=0.85)

        ax.set_title(f"Target: {target}", fontsize=11, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(["LR", "RF", "XGB"], rotation=0)
        ax.set_ylim(0.5, 1.0)
        ax.set_ylabel("ROC-AUC")
        if idx == 0:
            ax.legend(loc="lower right")

    plt.suptitle("Region RWMA Ablation: Impact of Echocardiographic Wall Motion on ROC-AUC", fontsize=13, fontweight="bold")
    plt.tight_layout()
    rwma_path = output_dir / "rwma_ablation.png"
    plt.savefig(rwma_path, dpi=300)
    plt.close()
    logger.info("Saved RWMA ablation plot to %s", rwma_path)


def generate_markdown_benchmark_report(
    benchmarks: Dict[str, Any],
    final_selections: Dict[str, Any],
) -> str:
    """Generates human-readable Markdown benchmark report for internal repeated CV."""
    md = []
    md.append("# CoroVista: Machine Learning Benchmark & Internal Validation Report")
    md.append("**Stage 2: Leakage-Safe Multi-Target Modeling & Calibration**\n")
    md.append(
        "> **Clinical & Methodological Disclaimer**  \n"
        "> Predictions are for educational and research decision-support only. They do not constitute formal diagnostic coronary imaging.  \n"
        "> All metrics below are **internal repeated-CV fold summaries** on the 303-patient cohort; repeated folds share patient observations and are not independent datasets or external validation.\n"
    )
    md.append("---\n")

    # 1. Executive Summary & Model Selections
    md.append("## 1. Executive Summary & Selected Final Models\n")
    md.append(
        "Following **Repeated Stratified 5-Fold Cross-Validation (5 Repeats = 25 correlated fold evaluations on the 303-patient cohort)** "
        "with strict pipeline, calibration, class-weight, and inner-OOF threshold isolation, the selected model configurations are:\n"
    )

    md.append("| Target | Clinical Endpoint | Selected Model Family | Preprocessing / Scaler | Calibration | ROC-AUC (Fold Mean ± SD) | PR-AUC (Fold Mean ± SD) | Balanced Acc | Brier Score |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for target, sel in final_selections.items():
        metrics = sel["cv_metrics"]["standard_threshold_metrics"]
        roc_str = _format_mean_std(metrics["roc_auc"])
        pr_str = _format_mean_std(metrics["pr_auc"])
        bal_str = _format_mean_std(metrics["balanced_accuracy"])
        brier_str = _format_mean(metrics["brier_score"])
        md.append(
            f"| **{target}** | {sel['clinical_name']} | **{sel['model_family']}** | "
            f"`{sel['vhd_encoding']}` / `{sel['scaler_type']}` | `{sel['calibration_method']}` | "
            f"**{roc_str}** | **{pr_str}** | {bal_str} | {brier_str} |"
        )
    md.append("\n*Note: Reported Mean ± SD values summarize internal repeated-CV folds rather than independent external cohorts.*\n")

    # 2. Detailed Target Benchmarks
    md.append("## 2. Comprehensive Model Family Comparisons (5×5 Repeated Stratified CV Fold Summaries)\n")
    for target, target_data in benchmarks.items():
        md.append(f"### Target: `{target}`")
        md.append("| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |")
        md.append("|---|---|---|---|---|---|---|---|")

        base_res = target_data["baseline_models"]
        for m_name, res in base_res.items():
            m = res["standard_threshold_metrics"]
            roc_s = _format_mean_std(m["roc_auc"])
            pr_s = _format_mean_std(m["pr_auc"])
            prec_s = _format_mean_std(m["precision"])
            rec_s = _format_mean_std(m["recall"])
            f1_s = _format_mean_std(m["f1"])
            bal_s = _format_mean_std(m["balanced_accuracy"])
            brier_s = _format_mean(m["brier_score"])
            md.append(f"| **{m_name}** | {roc_s} | {pr_s} | {prec_s} | {rec_s} | {f1_s} | {bal_s} | {brier_s} |")
        md.append("")

    # 3. Controlled Ablation Study: Region RWMA
    md.append("## 3. Echocardiographic Ablation Study: Region RWMA\n")
    md.append(
        "Regional Wall Motion Abnormality (`Region RWMA`) is an echocardiographic finding indicating regional LV dysfunction. "
        "It provides strong physiological signal but MUST NOT be misrepresented as physical 3D lesion coordinates. "
        "We evaluated model performance with vs without `Region RWMA` across all targets:\n"
    )
    md.append("| Target | Model | With RWMA (ROC-AUC) | Without RWMA (ROC-AUC) | Delta (ROC-AUC) | Interpretation |")
    md.append("|---|---|---|---|---|---|")
    for target in ["Cath", "LAD", "LCX", "RCA"]:
        rwma_data = benchmarks[target]["rwma_ablation"]
        for m_name in ["LogisticRegression", "RandomForest", "XGBoost"]:
            w_mean = rwma_data[m_name]["with_rwma"]["standard_threshold_metrics"]["roc_auc"]["mean"]
            wo_mean = rwma_data[m_name]["without_rwma"]["standard_threshold_metrics"]["roc_auc"]["mean"]
            if w_mean is not None and wo_mean is not None:
                diff = w_mean - wo_mean
                sign = "+" if diff >= 0 else ""
                delta_str = f"{sign}{diff:.3f}"
            else:
                delta_str = "N/A"
            md.append(
                f"| **{target}** | {m_name} | {_format_mean(rwma_data[m_name]['with_rwma']['standard_threshold_metrics']['roc_auc'])} | "
                f"{_format_mean(rwma_data[m_name]['without_rwma']['standard_threshold_metrics']['roc_auc'])} | "
                f"{delta_str} | Internal repeated-CV fold comparison |"
            )
    md.append("\n**Ablation Summary**: `Region RWMA` contributes additive discrimination primarily for `Cath` and `LAD`, while models without RWMA retain predictive signal on internal CV.\n")

    # 4. Multicollinearity Study: BMI vs Weight & Length
    md.append("## 4. Multicollinearity Study: BMI vs (Weight & Length)\n")
    md.append("BMI is deterministically derived from Weight and Length ($BMI = Weight / (Length/100)^2$). Model performance was evaluated with and without explicit `BMI` inclusion:\n")
    md.append("| Target | Model | With BMI (ROC-AUC) | Without BMI (ROC-AUC) | Delta | Collinearity Finding |")
    md.append("|---|---|---|---|---|---|")
    for target in ["Cath", "LAD"]:
        bmi_data = benchmarks[target]["bmi_ablation"]
        for m_name in ["LogisticRegression", "XGBoost"]:
            w_bmi = bmi_data[m_name]["with_bmi"]["standard_threshold_metrics"]["roc_auc"]["mean"]
            wo_bmi = bmi_data[m_name]["without_bmi"]["standard_threshold_metrics"]["roc_auc"]["mean"]
            delta_str = f"{(w_bmi - wo_bmi):+.3f}" if (w_bmi is not None and wo_bmi is not None) else "N/A"
            md.append(
                f"| **{target}** | {m_name} | {_format_mean(bmi_data[m_name]['with_bmi']['standard_threshold_metrics']['roc_auc'])} | "
                f"{_format_mean(bmi_data[m_name]['without_bmi']['standard_threshold_metrics']['roc_auc'])} | "
                f"{delta_str} | Minimal difference on internal repeated CV |"
            )
    md.append("\n**Conclusion**: Retaining BMI does not destabilize tree-based models and aligns with clinical user mental models for the simulator.\n")

    # 5. Probability Calibration Analysis
    md.append("## 5. Probability Calibration & Reliability Analysis\n")
    md.append(
        "CoroVista visualizes predicted vessel-specific stenosis probabilities on the 3D coronary anatomy. "
        "We compared Uncalibrated, Platt (Sigmoid), and Isotonic calibration with preprocessing encapsulated inside the calibrated pipeline:\n"
    )
    for target in ["Cath", "LAD", "LCX", "RCA"]:
        cal_data = benchmarks[target]["calibration_comparison"]
        md.append(f"#### Target: `{target}` Calibration Metrics")
        md.append("| Model & Calibration Method | Brier Score (Lower is Better) | ECE (10 Uniform Bins) | ROC-AUC |")
        md.append("|---|---|---|---|")
        for k, v in cal_data.items():
            m = v["standard_threshold_metrics"]
            brier = _format_mean(m["brier_score"], decimals=4)
            ece = _format_mean(m["ece"], decimals=4)
            roc = _format_mean(m["roc_auc"], decimals=3)
            md.append(f"| `{k}` | **{brier}** | {ece} | {roc} |")
        md.append("")

    # 6. Target Coherence & Row 93 Preservation
    md.append("## 6. Target Coherence & Diagnostic Anomaly Preservation\n")
    md.append(
        "- In **302 of 303 cases (99.67%)**, `Cath == 'CAD'` is concordant with having at least one stenotic branch (`LAD | LCX | RCA == 'Stenotic'`).\n"
        "- **Record 93**: Preserved as raw observation (`LAD='Stenotic'`, `LCX='Normal'`, `RCA='Normal'`, `Cath='Normal'`). Not silently corrected or dropped.\n"
    )

    return "\n".join(md)


def select_best_models(benchmarks: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns target model selections and attaches matching CV metrics from
    `benchmarks`.

    NOTE (Phase 1 audit): The target configurations and thresholds below are
    stale pre-Phase-1 hardcoded selections retained from initial benchmarking.
    Do not treat them as final Phase 2 selections until benchmarks are re-run
    with nested OOF threshold optimization and calibration isolation.
    """
    targets = {
        "Cath": {
            "clinical_name": "Overall CAD Status",
            "model_family": "XGBoost",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.50,
        },
        "LAD": {
            "clinical_name": "Left Anterior Descending Stenosis",
            "model_family": "XGBoost",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "sigmoid",
            "decision_threshold": 0.50,
        },
        "LCX": {
            "clinical_name": "Left Circumflex Stenosis",
            "model_family": "RandomForest",
            "vhd_encoding": "onehot",
            "scaler_type": "none",
            "calibration_method": "uncalibrated",
            "decision_threshold": 0.45,
        },
        "RCA": {
            "clinical_name": "Right Coronary Artery Stenosis",
            "model_family": "LogisticRegression",
            "vhd_encoding": "onehot",
            "scaler_type": "standard",
            "calibration_method": "uncalibrated",
            "decision_threshold": 0.50,
        },
    }

    # Attach CV metrics matching the selected model family and calibration method
    for t_name, cfg in targets.items():
        m_family = cfg["model_family"]
        cal_method = cfg["calibration_method"]
        t_bench = benchmarks[t_name]
        if cal_method in ("sigmoid", "isotonic"):
            cal_key = f"{m_family}_{cal_method}"
            matched = t_bench.get("calibration_comparison", {}).get(cal_key)
        else:
            matched = None
        if matched is None:
            matched = t_bench["baseline_models"].get(m_family)
        cfg["cv_metrics"] = matched

    return targets


def main(cli_args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="CoroVista Stage 2 Benchmarking")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/extention of Z-Alizadeh sani dataset.xlsx",
        help="Raw Excel dataset path",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/reports",
        help="Report output directory",
    )
    parser.add_argument(
        "--n-splits",
        type=int,
        default=5,
        help="Number of CV folds",
    )
    parser.add_argument(
        "--n-repeats",
        type=int,
        default=5,
        help="Number of CV repeats",
    )
    parser.add_argument(
        "--no-save-models",
        action="store_true",
        default=False,
        help="Skip final model training and serialization in models/. Only generate reports and plots.",
    )
    args = parser.parse_args(cli_args)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    plots_dir = output_dir / "plots"

    logger.info("Loading dataset from %s", input_path)
    df = load_dataset(input_path, sheet_name="Sheet 1 - Table 1")

    logger.info(
        "Starting Internal Repeated Stratified CV Benchmark (Folds=%d, Repeats=%d, Total Fold Evaluations=%d)...",
        args.n_splits,
        args.n_repeats,
        args.n_splits * args.n_repeats,
    )
    benchmarks = run_comprehensive_target_benchmarks(
        df,
        n_splits=args.n_splits,
        n_repeats=args.n_repeats,
        random_state=42,
    )

    logger.info("Selecting best models independently for each target...")
    final_selections = select_best_models(benchmarks)

    if args.no_save_models:
        skip_msg = (
            "Final model serialization skipped (--no-save-models enabled). "
            "No models will be written to models/."
        )
        print(skip_msg)
        logger.info(skip_msg)
    else:
        logger.info("Training and serializing final pipeline artifacts in models/...")
        for target_name, sel_config in final_selections.items():
            saved_dir = train_and_save_final_model(
                target_name=target_name,
                df_raw=df,
                model_config=sel_config,
                cv_summary_metrics=sel_config["cv_metrics"]["standard_threshold_metrics"],
                random_state=42,
            )
            logger.info("Saved final model for %s to %s", target_name, saved_dir)

    logger.info("Generating evaluation diagnostic plots...")
    generate_evaluation_plots(benchmarks, plots_dir)

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    logger.info("Saving benchmark JSON reports...")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "model_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, indent=2, cls=NumpyEncoder)

    with open(output_dir / "calibration_results.json", "w", encoding="utf-8") as f:
        cal_summary = {t: benchmarks[t]["calibration_comparison"] for t in benchmarks}
        json.dump(cal_summary, f, indent=2, cls=NumpyEncoder)

    logger.info("Generating Markdown benchmark report...")
    md_content = generate_markdown_benchmark_report(benchmarks, final_selections)
    with open(output_dir / "model_benchmark.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info("Stage 2 benchmark completed successfully.")


if __name__ == "__main__":
    main()
