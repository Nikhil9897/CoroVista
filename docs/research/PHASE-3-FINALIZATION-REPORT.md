# CoroVista — Phase 3 Finalization Report
## Final Model Reconciliation, Serialization, Verification & Production Promotion

**Project Title:** Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness  
**Cohort:** Z-Alizadeh Sani Dataset (303 patients, 54 eligible clinical predictive features)  
**Evaluation Protocol:** Repeated Stratified $K$-Fold (5 splits $\times$ 5 repeats = 25 folds), nested inner out-of-fold (OOF) threshold selection, internal validation (correlated folds; no external validation)  
**Date of Finalization:** November 15, 2026  
**Status:** **COMPLETE**

---

## 1. Executive Summary

Phase 3 of the CoroVista research pipeline has been finalized end-to-end:
1. **Benchmark Reproduction:** Completed without errors (28m 49s runtime) in `data/reports/reproduction_audit/`. Preprocessing encapsulation inside cross-validation, partition-isolated class weights, and nested inner-OOF threshold tuning were rigorously verified with zero outer-fold leakage.
2. **Evidence-Based Reconciliation:** Selected final target-specific models across discrimination (ROC-AUC, PR-AUC), probability calibration (Brier score, ECE), clinical sensitivity (recall), and balanced accuracy across repeated-CV fold distributions.
3. **Staging Serialization:** Serialized complete pipeline artifacts and audit metadata to staging directory `models/phase3_release/{cad,lad,lcx,rca}/`.
4. **Fresh-Process Verification:** Independently verified model unpickling, preprocessing integrity, calibration wrappers, threshold enforcement (RCA: 0.35, others: 0.50), and absence of in-memory training dependencies.
5. **Inference Smoke Testing:** Verified continuous probability generation in $[0, 1]$, finite bounds, threshold boundary classifications, and label mappings across representative patient profiles.
6. **Production Promotion:** Safely backed up previous production models to `models/backup_pre_phase3/` and promoted the staged Phase 3 pipelines to `models/{cad,lad,lcx,rca}/`.
7. **Regression Testing:** All 58 test suite components and production inference verification scripts passed with 100% success and 0 Ruff violations.

---

## 2. Final Reconciled Model Configurations

The final configurations approved and serialized for production deployment are summarized below:

| Target | Clinical Name | Model Family | Preprocessing | Calibration Method | Operating Threshold | Benchmark Section Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cath** | Overall CAD Status | **XGBoost** | One-Hot, None | **Sigmoid** (Platt) | **0.50** | `calibration_comparison.XGBoost_sigmoid` |
| **LAD** | Left Anterior Descending | **XGBoost** | One-Hot, None | **Sigmoid** (Platt) | **0.50** | `calibration_comparison.XGBoost_sigmoid` |
| **LCX** | Left Circumflex | **XGBoost** | One-Hot, None | **Uncalibrated** | **0.50** | `baseline_models.XGBoost` |
| **RCA** | Right Coronary Artery | **LogisticRegression** | One-Hot, StandardScaler | **Sigmoid** (Platt) | **0.35** | `calibration_comparison.LogisticRegression_sigmoid` |

---

## 3. Repeated-CV Benchmark Performance Evidence

> **Methodological Note:** Values below report internal validation **Repeated-CV Fold Mean $\pm$ Standard Deviation across 25 correlated folds** on the 303-patient cohort. Repeated folds share patient partitions and do not constitute independent external validation or formal confidence intervals.

### Primary Discrimination & Calibration Metrics

| Target | Selected Model | Calibration | Threshold | ROC-AUC (Mean $\pm$ SD) | PR-AUC (Mean $\pm$ SD) | Brier Score (Mean $\pm$ SD) | ECE (Mean $\pm$ SD) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cath** | XGBoost | Sigmoid | 0.50 | **$0.912 \pm 0.040$** | **$0.960 \pm 0.020$** | **$0.1034 \pm 0.0246$** | **$0.1004 \pm 0.0222$** |
| **LAD** | XGBoost | Sigmoid | 0.50 | **$0.844 \pm 0.052$** | **$0.882 \pm 0.046$** | **$0.1609 \pm 0.0221$** | **$0.1326 \pm 0.0386$** |
| **LCX** | XGBoost | Uncalibrated | 0.50 | **$0.736 \pm 0.062$** | **$0.617 \pm 0.082$** | **$0.2054 \pm 0.0235$** | **$0.1366 \pm 0.0309$** |
| **RCA** | Logistic Regression | Sigmoid | 0.35 | **$0.716 \pm 0.059$** | **$0.610 \pm 0.076$** | **$0.2060 \pm 0.0147$** | **$0.1000 \pm 0.0315$** |

### Threshold-Specific Operating Metrics Breakdown

Comparison of performance evaluated at the standard arbitrary cutoff ($0.50$) versus the selected empirical operating cutoff:

| Target | Operating Threshold | Operating $F_1$ (Mean $\pm$ SD) | Operating Recall (Sensitivity) | Operating Balanced Accuracy | Standard 0.50 $F_1$ | Standard 0.50 Recall | Standard 0.50 Balanced Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cath** | **0.50** (Standard) | $0.908 \pm 0.028$ | $92.1\% \pm 3.5\%$ | $82.6\% \pm 5.0\%$ | $0.908 \pm 0.028$ | $92.1\% \pm 3.5\%$ | $82.6\% \pm 5.0\%$ |
| **LAD** | **0.50** (Standard) | $0.824 \pm 0.036$ | $85.7\% \pm 6.5\%$ | $77.3\% \pm 5.2\%$ | $0.824 \pm 0.036$ | $85.7\% \pm 6.5\%$ | $77.3\% \pm 5.2\%$ |
| **LCX** | **0.50** (Standard) | $0.605 \pm 0.073$ | $61.6\% \pm 9.7\%$ | $67.4\% \pm 5.5\%$ | $0.605 \pm 0.073$ | $61.6\% \pm 9.7\%$ | $67.4\% \pm 5.5\%$ |
| **RCA** | **0.35** (Tuned) | **$0.604 \pm 0.051$** | **$79.5\% \pm 10.7\%$** | **$64.4\% \pm 5.6\%$** | $0.403 \pm 0.085$ | $31.2\% \pm 8.4\%$ | $58.8\% \pm 4.9\%$ |

*Note on LCX:* When screening sensitivity is prioritized, an alternative operating threshold of $0.35$ (inner-OOF mean $0.345$) increases Recall to $79.4\% \pm 11.8\%$ and $F_1$ to $0.622 \pm 0.063$, with Balanced Accuracy at $65.1\% \pm 6.4\%$.

---

## 4. Scientific Rationale & Trade-Offs

### A. Cath (Overall CAD Status)
* **Prevalence:** 71.3% (216 positive / 87 negative).
* **Rationale:** XGBoost with Sigmoid Platt calibration minimizes both Brier score ($0.1034$) and ECE ($0.1004$) across all evaluated models. ROC-AUC ($0.912$) and PR-AUC ($0.960$) demonstrate strong ranking capability. Operating cutoff $0.50$ is congruent with the inner-OOF tuned threshold mean ($0.491$), providing $92.1\%$ sensitivity and $89.5\%$ precision.

### B. LAD (Left Anterior Descending Stenosis)
* **Prevalence:** 58.4% (177 positive / 126 negative).
* **Trade-off Analysis (Random Forest vs XGBoost):**
  * *Discrimination:* Random Forest maintains a very small, non-significant ranking margin (ROC-AUC $0.853 \pm 0.051$ vs $0.844 \pm 0.052$; PR-AUC $0.885 \pm 0.045$ vs $0.882 \pm 0.046$; delta $< 0.009$, well within 1 SD).
  * *Calibration:* Calibrated XGBoost is clearly superior in probability reliability (Brier $0.1609$ vs $0.1674$; ECE $0.1326$ vs $0.1486$).
  * *Clinical Sensitivity:* XGBoost achieves higher recall at $0.50$ ($85.7\% \pm 6.5\%$ vs $85.2\% \pm 6.3\%$).
  * *Explainability:* XGBoost enables exact C++ TreeSHAP unwrapping via `corovista.explainability`.
* **Conclusion:** Retained XGBoost + Sigmoid for superior calibration and explainability integration.

### C. LCX (Left Circumflex Stenosis)
* **Prevalence:** 39.3% (119 positive / 184 negative).
* **Honest Evaluation:** XGBoost shows modestly higher observed fold-mean metrics than Random Forest (ROC-AUC $0.736$ vs $0.725$; PR-AUC $0.617$ vs $0.609$; Brier $0.2054$ vs $0.2098$). These differences are small relative to cross-fold variance ($\text{SD} \sim 0.06\text{--}0.08$) and do **not** imply statistical significance.
* **Calibration Choice:** Sigmoid and Isotonic calibration compress predicted probabilities on this minority target, causing sensitivity at $0.50$ to collapse to $42.2\%$. Uncalibrated XGBoost preserves higher balanced accuracy ($67.4\%$) and precision ($60.2\%$).

### D. RCA (Right Coronary Artery Stenosis)
* **Prevalence:** 37.6% (114 positive / 189 negative).
* **Threshold Reconciliation ($0.303$ vs $0.319$):**
  * Baseline uncalibrated Logistic Regression has inner-OOF threshold mean of $0.3032 \pm 0.0774$ (range $[0.21, 0.48]$).
  * Sigmoid-calibrated Logistic Regression (`LogisticRegression_sigmoid`) has inner-OOF threshold mean of $0.3188 \pm 0.0372$ (range $[0.20, 0.37]$). Platt calibration stabilizes threshold variance by more than $50\%$.
* **Operating Cutoff Selection ($0.35$):**
  * At standard $0.50$, Platt calibration compresses probabilities, causing sensitivity collapse (Recall $31.2\% \pm 8.4\%$, $F_1 = 0.403 \pm 0.085$).
  * Setting operating threshold to $0.35$ sits within 1 SD of the inner-OOF distribution ($0.319 + 0.037 = 0.356$) and well within the empirical range $[0.20, 0.37]$.
  * At $0.35$, sensitivity surges to **$79.5\% \pm 10.7\%$**, $F_1$ reaches **$0.604 \pm 0.051$**, and balanced accuracy improves to **$64.4\% \pm 5.6\%$**.

---

## 5. Artifact Inventory & Staging Structure

```
models/
├── backup_pre_phase3/           # Safe backup of historical production artifacts
│   ├── cad/                     # Historical CAD model & metadata
│   ├── lad/                     # Historical LAD model & metadata
│   ├── lcx/                     # Historical LCX model & metadata
│   └── rca/                     # Historical RCA model & metadata
├── phase3_release/              # Staging directory for newly trained Phase 3 models
│   ├── cad/                     # XGBoost + Sigmoid (pipeline.joblib: 340.8 KB, metadata.json: 8.0 KB)
│   ├── lad/                     # XGBoost + Sigmoid (pipeline.joblib: 355.2 KB, metadata.json: 8.0 KB)
│   ├── lcx/                     # XGBoost Uncalibrated (pipeline.joblib: 122.6 KB, metadata.json: 8.3 KB)
│   └── rca/                     # LogisticRegression + Sigmoid (pipeline.joblib: 25.1 KB, metadata.json: 8.4 KB)
└── [Production Paths]           # Promoted Phase 3 models
    ├── cad/
    ├── lad/
    ├── lcx/
    └── rca/
```

### Metadata Fields Recorded
Every serialized `metadata.json` artifact includes:
1. `target`: Prediction target identifier (`Cath`, `LAD`, `LCX`, `RCA`).
2. `model_family`: Machine learning model family (`XGBoost`, `LogisticRegression`).
3. `vhd_encoding`, `scaler_type`, `drop_rwma`, `drop_bmi`: Complete preprocessing pipeline parameters.
4. `calibration_method`: Calibration wrapper (`sigmoid`, `uncalibrated`).
5. `decision_threshold`: Verified operating cutoff ($0.50$ for Cath, LAD, LCX; $0.35$ for RCA).
6. `dataset_identifier`: `"Z-Alizadeh Sani extension cohort (303 patients, 54 predictive features)"`.
7. `training_timestamp`: ISO 8601 UTC timestamp.
8. `software_versions`: Python 3.11.18, scikit-learn 1.7.2, xgboost 3.2.0, joblib 1.6.0.
9. `benchmark_protocol`: `"RepeatedStratifiedKFold (5 splits x 5 repeats = 25 folds), nested inner-OOF threshold selection, internal repeated CV (correlated folds; no external validation)"`.
10. `training_samples` & `training_positives`: Exact cohort sample and class counts (zero patient-level identifiers or clinical records).
11. `input_features` & `feature_schema`: Complete 55-column feature names and data types.
12. `cross_validation_metrics`: Full metrics bundle from repeated-CV validation.

---

## 6. Fresh-Process Verification & Smoke Testing Results

### Fresh-Process Unpickling Verification
Executed in an isolated Python interpreter without prior state:
* `models/phase3_release/cad`: Loaded `CalibratedClassifierCV` (3 inner folds, `preprocessing` + `classifier` steps, threshold 0.50).
* `models/phase3_release/lad`: Loaded `CalibratedClassifierCV` (3 inner folds, `preprocessing` + `classifier` steps, threshold 0.50).
* `models/phase3_release/lcx`: Loaded `Pipeline` (`preprocessing` + `classifier` steps, threshold 0.50).
* `models/phase3_release/rca`: Loaded `CalibratedClassifierCV` (3 inner folds, `preprocessing` + `classifier` steps, threshold 0.35).

### Prediction Smoke Tests on Promoted Models
Smoke tests evaluated 3 representative patient rows across the complete four-target inference engine:

```
[Patient Index 0 - Typical Presentation]
  CATH: prob = 0.7862  ->  Prediction: CAD       (threshold = 0.50, model = XGBoost)
  LAD : prob = 0.6156  ->  Prediction: Stenotic  (threshold = 0.50, model = XGBoost)
  LCX : prob = 0.1413  ->  Prediction: Normal    (threshold = 0.50, model = XGBoost)
  RCA : prob = 0.3720  ->  Prediction: Stenotic  (threshold = 0.35, model = LogisticRegression)

[Patient Index 10 - High Multi-Vessel Risk Profile]
  CATH: prob = 0.9298  ->  Prediction: CAD       (threshold = 0.50, model = XGBoost)
  LAD : prob = 0.6512  ->  Prediction: Stenotic  (threshold = 0.50, model = XGBoost)
  LCX : prob = 0.8010  ->  Prediction: Stenotic  (threshold = 0.50, model = XGBoost)
  RCA : prob = 0.3591  ->  Prediction: Stenotic  (threshold = 0.35, model = LogisticRegression)

[Patient Index 93 - Isolated LAD Stenosis Presentation]
  CATH: prob = 0.6739  ->  Prediction: CAD       (threshold = 0.50, model = XGBoost)
  LAD : prob = 0.8495  ->  Prediction: Stenotic  (threshold = 0.50, model = XGBoost)
  LCX : prob = 0.2779  ->  Prediction: Normal    (threshold = 0.50, model = XGBoost)
  RCA : prob = 0.5170  ->  Prediction: Stenotic  (threshold = 0.35, model = LogisticRegression)
```

All continuous probabilities satisfied $0.0 \le p \le 1.0$, were finite, and matched discrete class labels under the respective decision thresholds.

---

## 7. Verification Test Suite Results

| Test Module | Scope | Tests Run | Result | Duration |
| :--- | :--- | :--- | :--- | :--- |
| `tests/test_inference.py` | Model loading, thresholds (0.35 RCA), schemas, determinism, leakage | 13 | **PASSED** | 3.42s |
| `tests/test_ml_pipeline.py` | Preprocessing, feature registry, zero-variance, dynamic class weights | 14 | **PASSED** | (combined) |
| `tests/test_benchmark_execution_safety.py` | `--no-save-models` flag, CLI parsing, models directory immutability | 4 | **PASSED** | 21.32s |
| `tests/test_dataset_audit.py` | Dataset loading, shape, leakage checks, missing value validation | 11 | **PASSED** | (combined) |
| `tests/test_explainability.py` | SHAP additivity, tree explainer, calibrated numerical reconstruction | 16 | **PASSED** | (combined) |
| `scripts/verify_inference.py` | End-to-end inference, patient SHAP, global SHAP plot exports | Script | **PASSED** | 3.20s |
| `ruff check` | Code style and formatting across all changed files | 7 files | **PASSED** | 0 errors |

**Total Unit/Integration Tests Passed:** 58 tests.

---

## 8. Explicit Scientific Limitations & Disclaimers

1. **Internal Cross-Validation Only:** All reported metrics were derived via internal repeated cross-validation on the 303-patient Z-Alizadeh Sani cohort from Tehran Heart Center. No external geographic, temporal, or demographic validation has been performed.
2. **Correlated Folds:** The 25 repeated cross-validation folds share patient samples. Metric standard deviations reflect variability across fold splits and do not constitute independent-sample confidence intervals.
3. **Full Dataset Serialization:** Model pipelines serialized into `models/` were trained on the complete 303-patient cohort for production inference. Performance on this training data does not represent an independent evaluation.
4. **Vessel-Specific Limitations:**
   * **LCX:** Demonstrates modest discrimination (ROC-AUC $0.736 \pm 0.062$, PR-AUC $0.617 \pm 0.082$).
   * **RCA:** Displays limited balanced accuracy ($64.4\% \pm 5.6\%$) even at the optimized operating cutoff ($0.35$).
5. **No Clinical Readiness Claim:** CoroVista is an academic research prototype intended for algorithmic transparency, calibration study, and 3D explainability analysis. It has **not** received regulatory clearance and must not be used as an autonomous medical diagnostic device.

---

## 9. Reproducibility Instructions

### Dry-Run Reconciled Model Summary
```bash
.venv/bin/python scripts/reconcile_and_save_models.py --no-save
```

### Staging Model Serialization
```bash
.venv/bin/python scripts/reconcile_and_save_models.py --output-dir models/phase3_release
```

### Full Inference & Explainability Production Verification
```bash
.venv/bin/python scripts/verify_inference.py
```

### Automated Unit & Regression Test Execution
```bash
.venv/bin/python -m pytest tests/test_inference.py tests/test_ml_pipeline.py tests/test_benchmark_execution_safety.py tests/test_dataset_audit.py tests/test_explainability.py -v
```

### Code Style & Linter Check
```bash
.venv/bin/ruff check ml/training/trainer.py scripts/reconcile_and_save_models.py scripts/run_benchmarks.py scripts/verify_inference.py src/corovista/inference/predictor.py tests/test_inference.py tests/test_benchmark_execution_safety.py
```
