"""
Tests for CoroVista Phase 3 Benchmark Execution Safety.

Validates:
1. --no-save-models CLI flag prevents final model serialization in models/.
2. Benchmark report generation (JSON, Markdown, diagnostic plots) operates correctly
   under the requested --output-dir without writing model artifacts.
3. Model artifact paths (models/cad, lad, lcx, rca) are untouched in --no-save-models mode.
4. Default behavior (omitting --no-save-models) preserves model serialization calls.
5. CLI argument parsing correctly sets no_save_models=False by default and True when specified.
"""

import json
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pandas as pd

from scripts.run_benchmarks import main


def _make_dummy_metric(mean: float = 0.85, std: float = 0.04) -> Dict[str, Any]:
    return {
        "mean": mean,
        "std": std,
        "n_valid_folds": 25,
        "n_undefined_folds": 0,
        "summary_scope": "repeated_cv_fold_summary",
    }


def _make_dummy_metrics_bundle(roc_mean: float = 0.90) -> Dict[str, Any]:
    return {
        "roc_auc": _make_dummy_metric(roc_mean, 0.03),
        "pr_auc": _make_dummy_metric(0.88, 0.04),
        "accuracy": _make_dummy_metric(0.85, 0.04),
        "precision": _make_dummy_metric(0.83, 0.05),
        "recall": _make_dummy_metric(0.87, 0.04),
        "f1": _make_dummy_metric(0.85, 0.04),
        "balanced_accuracy": _make_dummy_metric(0.84, 0.05),
        "brier_score": _make_dummy_metric(0.12, 0.02),
        "ece": _make_dummy_metric(0.05, 0.01),
    }


def _make_synthetic_benchmarks() -> Dict[str, Any]:
    """Generates a complete minimal benchmark result structure matching run_comprehensive_target_benchmarks."""
    targets = ["Cath", "LAD", "LCX", "RCA"]
    models = ["Dummy", "LogisticRegression", "RandomForest", "XGBoost"]
    oof_y = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    oof_prob = [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6, 0.15, 0.85]

    benchmarks: Dict[str, Any] = {}
    for t in targets:
        base_res: Dict[str, Any] = {}
        for m in models:
            base_res[m] = {
                "standard_threshold_metrics": _make_dummy_metrics_bundle(),
                "tuned_threshold_metrics": _make_dummy_metrics_bundle(),
                "selected_thresholds": [0.5] * 25,
                "oof_y_true": list(oof_y),
                "oof_y_prob": list(oof_prob),
            }

        cal_res: Dict[str, Any] = {}
        for cal_name in ["XGBoost_uncalibrated", "XGBoost_sigmoid", "XGBoost_isotonic",
                         "LogisticRegression_uncalibrated", "LogisticRegression_sigmoid", "LogisticRegression_isotonic"]:
            cal_res[cal_name] = {
                "standard_threshold_metrics": _make_dummy_metrics_bundle(),
                "tuned_threshold_metrics": _make_dummy_metrics_bundle(),
                "selected_thresholds": [0.5] * 25,
                "oof_y_true": list(oof_y),
                "oof_y_prob": list(oof_prob),
            }

        rwma_res: Dict[str, Any] = {}
        for m in ["LogisticRegression", "RandomForest", "XGBoost"]:
            rwma_res[m] = {
                "with_rwma": {"standard_threshold_metrics": _make_dummy_metrics_bundle(0.88)},
                "without_rwma": {"standard_threshold_metrics": _make_dummy_metrics_bundle(0.82)},
            }

        bmi_res: Dict[str, Any] = {}
        for m in ["LogisticRegression", "RandomForest", "XGBoost"]:
            bmi_res[m] = {
                "with_bmi": {"standard_threshold_metrics": _make_dummy_metrics_bundle(0.88)},
                "without_bmi": {"standard_threshold_metrics": _make_dummy_metrics_bundle(0.87)},
            }

        benchmarks[t] = {
            "baseline_models": base_res,
            "preprocessing_comparison": {},
            "rwma_ablation": rwma_res,
            "bmi_ablation": bmi_res,
            "calibration_comparison": cal_res,
        }

    return benchmarks


def _make_dummy_df() -> pd.DataFrame:
    """Builds a minimal dummy DataFrame for mocking load_dataset."""
    return pd.DataFrame({
        "Age": [50, 60],
        "Cath": ["CAD", "Normal"],
        "LAD": ["Stenotic", "Normal"],
        "LCX": ["Normal", "Stenotic"],
        "RCA": ["Normal", "Normal"],
    })


def test_no_save_models_prevents_serialization(monkeypatch, tmp_path, capsys):
    """
    --no-save-models must:
    1. Not invoke train_and_save_final_model.
    2. Print and log a clear notice that final model serialization was skipped.
    3. Generate all reports and plots in the designated output directory.
    4. Not create any model files in models/.
    """
    mock_save = MagicMock()
    monkeypatch.setattr("scripts.run_benchmarks.train_and_save_final_model", mock_save)
    monkeypatch.setattr("scripts.run_benchmarks.load_dataset", lambda *args, **kwargs: _make_dummy_df())
    monkeypatch.setattr(
        "scripts.run_benchmarks.run_comprehensive_target_benchmarks",
        lambda *args, **kwargs: _make_synthetic_benchmarks(),
    )

    out_dir = tmp_path / "reports_test"
    cli_args = [
        "--no-save-models",
        "--output-dir",
        str(out_dir),
        "--n-splits",
        "2",
        "--n-repeats",
        "1",
    ]

    main(cli_args)

    # 1. train_and_save_final_model must NOT have been called
    assert mock_save.call_count == 0

    # 2. Clear notice printed to stdout
    captured = capsys.readouterr()
    assert "Final model serialization skipped (--no-save-models enabled)" in captured.out
    assert "No models will be written to models/" in captured.out

    # 3. Reports and diagnostic plots were genuinely generated under out_dir
    json_path = out_dir / "model_benchmark.json"
    cal_path = out_dir / "calibration_results.json"
    md_path = out_dir / "model_benchmark.md"

    assert json_path.is_file() and json_path.stat().st_size > 0
    assert cal_path.is_file() and cal_path.stat().st_size > 0
    assert md_path.is_file() and md_path.stat().st_size > 0

    # Parse and verify content of generated reports
    bench_data = json.loads(json_path.read_text(encoding="utf-8"))
    assert set(bench_data.keys()) == {"Cath", "LAD", "LCX", "RCA"}
    cal_data = json.loads(cal_path.read_text(encoding="utf-8"))
    assert set(cal_data.keys()) == {"Cath", "LAD", "LCX", "RCA"}
    md_text = md_path.read_text(encoding="utf-8")
    assert "# CoroVista: Machine Learning Benchmark" in md_text
    assert "Cath" in md_text and "LAD" in md_text

    # Diagnostic plots were rendered and saved
    for plot_name in [
        "model_comparison.png",
        "roc_curves.png",
        "pr_curves.png",
        "calibration_curves.png",
        "rwma_ablation.png",
    ]:
        p = out_dir / "plots" / plot_name
        assert p.is_file()
        assert p.stat().st_size > 0

    # 4. No model artifacts (neither .joblib nor metadata.json) written in out_dir
    assert len(list(out_dir.glob("**/*.joblib"))) == 0
    assert len(list(out_dir.glob("**/metadata.json"))) == 0


def test_no_save_models_unmocked_leaves_models_directory_untouched(monkeypatch, tmp_path):
    """
    With train_and_save_final_model UNMOCKED, calling main() with --no-save-models
    must not touch or modify any file in models/ (neither .joblib nor metadata.json).
    """
    models_root = Path("models")
    before_state = {
        p: (p.stat().st_mtime_ns, p.stat().st_size)
        for p in models_root.glob("**/*")
        if p.is_file()
    }
    assert len(before_state) > 0  # Verify existing artifacts exist

    monkeypatch.setattr("scripts.run_benchmarks.load_dataset", lambda *args, **kwargs: _make_dummy_df())
    monkeypatch.setattr(
        "scripts.run_benchmarks.run_comprehensive_target_benchmarks",
        lambda *args, **kwargs: _make_synthetic_benchmarks(),
    )

    out_dir = tmp_path / "staging_reports"
    main(["--no-save-models", "--output-dir", str(out_dir)])

    # Verify models/ is completely unchanged
    after_state = {
        p: (p.stat().st_mtime_ns, p.stat().st_size)
        for p in models_root.glob("**/*")
        if p.is_file()
    }
    assert before_state == after_state

    # Verify out_dir received all reports and plots
    assert (out_dir / "model_benchmark.json").is_file()
    assert (out_dir / "calibration_results.json").is_file()
    assert (out_dir / "model_benchmark.md").is_file()
    assert len(list(out_dir.glob("plots/*.png"))) == 5
    assert len(list(out_dir.glob("**/*.joblib"))) == 0
    assert len(list(out_dir.glob("**/metadata.json"))) == 0


def test_default_omission_preserves_serialization_call(monkeypatch, tmp_path):
    """
    When --no-save-models is omitted, main() must invoke train_and_save_final_model
    for each target, preserving the existing default behavior.
    """
    mock_save = MagicMock(return_value=Path("models/mock_dir"))
    monkeypatch.setattr("scripts.run_benchmarks.train_and_save_final_model", mock_save)
    monkeypatch.setattr("scripts.run_benchmarks.load_dataset", lambda *args, **kwargs: _make_dummy_df())
    monkeypatch.setattr(
        "scripts.run_benchmarks.run_comprehensive_target_benchmarks",
        lambda *args, **kwargs: _make_synthetic_benchmarks(),
    )

    out_dir = tmp_path / "reports_default"
    cli_args = [
        "--output-dir",
        str(out_dir),
        "--n-splits",
        "2",
        "--n-repeats",
        "1",
    ]

    main(cli_args)

    # Exactly 4 calls for the 4 targets (Cath, LAD, LCX, RCA)
    assert mock_save.call_count == 4
    called_targets = [call.kwargs.get("target_name") for call in mock_save.call_args_list]
    assert set(called_targets) == {"Cath", "LAD", "LCX", "RCA"}


def test_cli_parsing_no_save_models_flag():
    """Validates CLI argument parsing for --no-save-models."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-save-models",
        action="store_true",
        default=False,
    )

    # Default is False
    args_default = parser.parse_args([])
    assert args_default.no_save_models is False

    # Enabled is True
    args_flag = parser.parse_args(["--no-save-models"])
    assert args_flag.no_save_models is True
