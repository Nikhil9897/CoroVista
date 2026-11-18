# CoroVista — Phase 5.1: Manuscript Evidence Matrix & Locked Scientific Results

**Manuscript Title:** Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness  
**Phase:** 5.1 (Manuscript Evidence Lock — Final Reconciled Edition)  
**Date of Lock:** November 15, 2026  
**Repository Branch:** `development`  
**Status:** **LOCKED, RECONCILED, AUDITED, AND FULLY TRACEABLE**  

---

## 1. Executive Overview & Evidence Inventory Purpose

This document establishes the definitive, audited scientific evidence inventory for authoring the research manuscript. It consolidates, verifies, and cross-references all empirical findings across Phase 3 (model benchmarking, calibration, threshold tuning, and serialization) and Phase 4 (explainability stability, prediction stability, uncertainty quantification, stress testing, feature ablation, and subgroup analysis).

Every numerical value in this matrix is mapped directly to authoritative source files, code implementations, and evaluation protocols. In accordance with clinical machine learning reporting standards (TRIPOD+AI) and strict scientific integrity principles:
1. **Strict Protocol Segregation:** Distinct evaluation protocols are never combined or conflated:
   - **25-fold repeated-CV fold distributions (Sample SD, `ddof=1`):** Primary standard for fold-level variability.
   - **25-fold repeated-CV fold distributions (Population SD, `ddof=0`):** Direct outputs from `aggregate_cv_metrics()` (`np.std`).
   - **Standard threshold ($\tau = 0.50$) classification performance.**
   - **Nested inner-fold tuned threshold classification performance.**
   - **Fixed production operating threshold ($\tau = 0.35$ for RCA) across 25 outer folds.**
   - **Five-repeat pooled out-of-fold evaluation metrics (Mean ± SD across $R=5$ repeats).**
   - **Consensus multi-repeat patient OOF metrics ($N=303$).**
2. **Sample Standard Deviation Preservation:** All primary 25-fold cross-validation tables report the sample standard deviation (`ddof=1`, dividing by $K - 1 = 24$, factor $\sqrt{25/24} \approx 1.0206$) to reflect fold-level resampling dispersion.
3. **Traceability:** Every claim is backed by a verified repository artifact (`.json`, `.csv`, `.py`, or `.md`).
4. **Boundary Honesty:** Limitations regarding single-center retrospective sampling, absence of external validation, correlated repeated folds, non-linear calibration spaces, and observational explainability are explicitly declared.

---

## 2. Targeted Numerical Discrepancy Reconciliation

During Phase 5.1 final audit, four specific numerical discrepancies between raw benchmark JSON outputs, calibration artifacts, Phase 3 reports, production metadata, and README summaries were investigated. Their mathematical root causes and authoritative resolutions are established below:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TARGETED DISCREPANCY RECONCILIATION SUMMARY                                         │
├───────────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│ Metric Dimension              │ Raw Artifact (ddof=0)    │ Bessel Corrected (ddof=1)│ Root Cause & Authoritative Status│
├───────────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ Cath ROC-AUC SD               │ 0.0396                   │ 0.0404                   │ np.std(ddof=0) vs sample SD      │
│ LAD ROC-AUC SD                │ 0.0518                   │ 0.0528                   │ np.std(ddof=0) vs sample SD      │
│ RCA Nested Tuned Recall SD    │ 0.1070                   │ 0.1092                   │ np.std(ddof=0) vs sample SD      │
│ RCA Nested Tuned Specificity SD│ 0.1400                  │ 0.1429 (not 0.1093)      │ True 25-fold SD vs copy typo     │
└───────────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

1. **Cath ROC-AUC Standard Deviation (0.0404 vs. 0.0396):**
   - **Source Code Origin:** In `ml/evaluation/metrics.py:299`, `aggregate_cv_metrics()` computes `"std": round(float(np.std(valid_vals)), 4)`. Numpy's default `np.std()` uses `ddof=0` (population standard deviation, dividing by $N=25$). This yielded **0.0396**, which was serialized into `data/reports/reproduction_audit/calibration_results.json`, `data/reports/model_benchmark.json`, and `models/cad/metadata.json`.
   - **Bessel Correction:** When computing the unbiased sample standard deviation (`ddof=1`, dividing by $N-1 = 24$), the value scales by $\sqrt{25/24} \approx 1.02062$, yielding $0.0396 \times 1.02062 = \mathbf{0.040416 \dots \approx 0.0404}$.
   - **Resolution:** The manuscript reports **$0.9123 \pm 0.0404$** as the primary sample SD (`ddof=1`), while explicitly disclosing the population SD ($0.0396$, `ddof=0`) from the raw code output.

2. **LAD ROC-AUC Standard Deviation (0.0528 vs. 0.0518):**
   - **Source Code Origin:** `np.std(valid_vals, ddof=0)` in `aggregate_cv_metrics()` yielded **0.0518**, serialized into `data/reports/reproduction_audit/calibration_results.json`, `data/reports/model_benchmark.json`, and `models/lad/metadata.json`.
   - **Bessel Correction:** Computing sample SD (`ddof=1`) yields $0.0518 \times \sqrt{25/24} = \mathbf{0.052868 \dots \approx 0.0528}$ (as reported in `README.md`).
   - **Resolution:** The manuscript reports **$0.8443 \pm 0.0528$** as the primary sample SD (`ddof=1`), while documenting the raw population SD ($0.0518$).

3. **RCA Nested Tuned Recall Standard Deviation (0.1092 vs. 0.1070):**
   - **Source Code Origin:** In `data/reports/reproduction_audit/calibration_results.json`, `tuned_threshold_metrics.recall.std` is recorded as **0.1070** (`ddof=0`).
   - **Bessel Correction:** Applying Bessel's correction yields $0.1070 \times \sqrt{25/24} = \mathbf{0.109206 \dots \approx 0.1092}$.
   - **Resolution:** The manuscript reports **$0.7946 \pm 0.1092$** for sample SD (`ddof=1`) and acknowledges the stored population SD ($0.1070$).

4. **RCA Nested Tuned Specificity Standard Deviation (0.1429 vs. 0.1093):**
   - **Source Code Origin:** In `ml/evaluation/metrics.py:275-285`, the `keys` aggregated by `aggregate_cv_metrics()` include only: `["roc_auc", "pr_auc", "accuracy", "precision", "recall", "f1", "balanced_accuracy", "brier_score", "ece"]`. **`specificity` was omitted from the aggregation dictionary.**
   - **Artifactual Value (0.1093):** During earlier preliminary table compilation, the recall sample SD ($0.1092 \approx 0.1093$) was mistakenly duplicated into the specificity column because specificity lacked a precomputed summary block.
   - **Recomputed Ground Truth:** Calculating specificity across all 25 outer test folds at their respective inner-OOF selected thresholds yields:
     - Mean Specificity: **0.4941**
     - Population Standard Deviation (`ddof=0`): **0.1400**
     - Sample Standard Deviation (`ddof=1`): **0.1429**
   - **Resolution:** The artifactual value `0.1093` is formally discarded. The true 25-fold outer-evaluation specificity is locked as **$0.4941 \pm 0.1429$** (`ddof=1`) and $0.4941 \pm 0.1400$ (`ddof=0`).

---

## 3. Authoritative Source Documents and Data Artifacts

| Artifact Identifier | Repository Path | Nature of File | Content / Scientific Role |
| :--- | :--- | :--- | :--- |
| **SRC-1** | `docs/research/PHASE-3-FINALIZATION-REPORT.md` | Markdown Report | Phase 3 model selection, calibration rationale, threshold reconciliation, and production deployment audit. |
| **SRC-2** | `docs/research/PHASE-4-EXPERIMENTS-REPORT.md` | Markdown Report | Phase 4 stability, uncertainty, robustness, ablation, and subgroup experimental findings. |
| **SRC-3** | `docs/research/PHASE-4-SCIENTIFIC-VALIDATION-ADDENDUM.md` | Markdown Report | Mathematical proof of metric reconciliation between Phase 3 and Phase 4, subgroup phrasing audit, and clinical triage boundary declarations. |
| **SRC-4** | `data/reports/phase4/summary/phase4_master_metrics.json` | JSON Master Artifact | Authoritative compiled machine-readable metrics for all Phase 4 experiments (Exp A through Exp E) and reconstruction checks. |
| **SRC-5** | `data/reports/phase4/summary/phase4_executive_summary.md` | Markdown Report | High-level scientific summary of Phase 4 research insights. |
| **SRC-6** | `data/reports/reproduction_audit/calibration_results.json` | JSON Reproduction Artifact | 25-fold cross-validation fold metrics, threshold selections, and calibration evaluations for baseline and calibrated models. |
| **SRC-7** | `data/reports/reproduction_audit/model_benchmark.json` | JSON Reproduction Artifact | Comprehensive 25-fold benchmark metrics across all model families (Dummy, LogisticRegression, RandomForest, XGBoost). |
| **SRC-8** | `data/reports/dataset_audit.json` & `.md` | JSON / MD Audit | Cohort shape, missingness, duplicate audit, column types, target distributions, and clinical category partitions. |
| **SRC-9** | `configs/feature_metadata.yaml` | YAML Configuration | Authoritative feature registry: schema types, zero-variance flags, normalization rules, and clinical groupings. |
| **SRC-10** | `models/{cad,lad,lcx,rca}/metadata.json` | JSON Model Metadata | Production-promoted model parameters, operating cutoffs, feature schemas, software versions, and recorded CV metrics. |
| **SRC-11** | `ml/training/trainer.py` & `pipeline.py` | Python Implementation | Leakage guards, deterministic cleaners, imputation, transformers, model estimators, and calibration wrappers. |
| **SRC-12** | `ml/training/benchmark.py` & `ml/evaluation/metrics.py` | Python Implementation | Repeated stratified K-fold harness, nested inner-OOF threshold selection, and metric aggregation algorithms. |
| **SRC-13** | `ml/research/` modules (`cv_protocol.py`, `shap_stability.py`, `prediction_stability.py`, `uncertainty.py`, `robustness.py`, `subgroup_analysis.py`) | Python Implementation | Experimental implementations for Phase 4 research dimensions. |

---

## 4. Manuscript Methodology Specification

### 4.1 Cohort Provenance and Study Population
- **Cohort Identifier:** Extended Z-Alizadeh Sani Cardiology Dataset.
- **Clinical Center:** Tehran Heart Center, Tehran, Iran (tertiary cardiovascular referral institution).
- **Study Design:** Retrospective cross-sectional diagnostic study.
- **Cohort Sample Size:** $N = 303$ consecutive patients referred for coronary catheterization.
- **Reference Standard:** Invasive Coronary Angiography (ICA). Significant coronary artery disease (CAD) defined as $\ge 50\%$ luminal diameter stenosis in $\ge 1$ major epicardial coronary vessel.
- **Target Definitions:**
  1. `Cath`: Significant CAD in any coronary artery ($\ge 50\%$ stenosis in $\ge 1$ vessel). $N_+ = 216$ (71.29%), $N_- = 87$ (28.71%).
  2. `LAD`: Stenosis $\ge 50\%$ in the Left Anterior Descending artery. $N_+ = 177$ (58.42%), $N_- = 126$ (41.58%).
  3. `LCX`: Stenosis $\ge 50\%$ in the Left Circumflex artery. $N_+ = 119$ (39.27%), $N_- = 184$ (60.73%).
  4. `RCA`: Stenosis $\ge 50\%$ in the Right Coronary Artery. $N_+ = 114$ (37.62%), $N_- = 189$ (62.38%).
- **Preservation of Record Index 93:** One patient record presents an unusual clinical diagnostic profile: `Cath = 'Normal'`, `LAD = 'Stenotic'`, `LCX = 'Normal'`, `RCA = 'Normal'`. In accordance with medical data integrity and clinical research ethics, this observation was preserved intact without manual relabeling, modification, or imputation.

### 4.2 Feature Schema Audit and Exclusion Rules
- **Total Workbook Columns:** 59 columns.
- **Excluded Ground-Truth Targets:** 4 columns (`Cath`, `LAD`, `LCX`, `RCA`).
- **Raw Input Feature Matrix:** 55 non-target clinical features.
- **Zero-Variance Feature Exclusion:** Exactly 1 feature, `Exertional CP`, exhibits zero variance across all 303 patients (100% constant `'N'`). It is deterministically excluded by `ClinicalFeatureCleaner`.
- **Active Predictive Features Entering Transformers:** Exactly **54 eligible clinical features**.
- **Design Matrix Dimensionality (Transformed):** Exactly **57 numerical features** following One-Hot encoding of nominal variables (`VHD` with 4 levels, `BBB` with 3 levels).
- **Clinical Domain Distribution (54 Active Features):**
  - Demographic: 4 (`Age`, `Weight`, `Length`, `Sex`)
  - History & Risk Habits: 7 (`DM`, `HTN`, `Current Smoker`, `EX-Smoker`, `FH`, `Obesity`, `CRF`)
  - Symptoms & Physical Examination: 12 (`BP`, `PR`, `Edema`, `Weak Peripheral Pulse`, `Lung rales`, `Systolic Murmur`, `Diastolic Murmur`, `Typical Chest Pain`, `Dyspnea`, `Function Class`, `Atypical`, `Nonanginal`, `LowTH Ang`)
  - Clinical Comorbidities: 3 (`CVA`, `Airway disease`, `Thyroid Disease`, `CHF`)
  - Laboratory Panels: 14 (`FBS`, `CR`, `TG`, `LDL`, `HDL`, `BUN`, `ESR`, `HB`, `K`, `Na`, `WBC`, `Lymph`, `Neut`, `PLT`)
  - Resting ECG Findings: 7 (`Q Wave`, `St Elevation`, `St Depression`, `Tinversion`, `LVH`, `Poor R Progression`, `BBB`)
  - Transthoracic Echocardiography (TTE): 3 (`EF-TTE`, `Region RWMA`, `VHD`)

### 4.3 Leakage Prevention and Preprocessing Architecture
- **Strict CV Encapsulation:** All statistical estimations (imputation medians, standard scalers, categorical encoders, and calibration mappings) are fit strictly within outer training folds. Outer test partitions remain completely unseen until inference.
- **Automated Leakage Guard:** `LeakageGuardTransformer` immediately halts execution if any of the four ground-truth target columns appear in the feature matrix $X$.
- **Imputation Strategy:**
  - Continuous/Ordinal numerical variables: `SimpleImputer(strategy="median")`.
  - Binary/Categorical variables: `SimpleImputer(strategy="most_frequent")`.
  - Audited dataset has 0 missing values; imputers function as defensive shields against test-time missingness.
- **Categorical Encoders:**
  - `Sex`: Normalized from raw string (`'Fmale'` typo corrected to 0; `'Male'` mapped to 1).
  - Binary strings (`'Y'`/`'N'`): Mapped deterministically to 1/0.
  - `VHD` (Valvular Heart Disease): Nominal One-Hot encoding (`'Normal'`, `'Mild'`, `'Moderate'`, `'Severe'`).
  - `BBB` (Bundle Branch Block): Nominal One-Hot encoding (`'N'`, `'LBBB'`, `'RBBB'`).
- **Feature Scaling:**
  - Tree-based models (XGBoost, RandomForest): No feature scaling (`scaler_type="none"`).
  - Regularized linear models (LogisticRegression): `StandardScaler()` fit within training folds.

### 4.4 Model Architectures and Hyperparameters
- **XGBoost (Cath, LAD, LCX):**
  - Architecture: `DynamicScalePosWeightXGBClassifier` wrapping `xgboost.XGBClassifier`.
  - Hyperparameters: `n_estimators=100`, `max_depth=3`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `eval_metric="logloss"`, `random_state=42`.
  - Dynamic Class Weighting: `scale_pos_weight = N_neg / N_pos`, dynamically computed strictly inside each outer training partition to prevent class prevalence leakage.
- **Logistic Regression (RCA):**
  - Architecture: `LogisticRegression`.
  - Hyperparameters: `solver="liblinear"`, `C=1.0`, `class_weight="balanced"`, `max_iter=1000`, `random_state=42`.
- **Random Forest (Benchmark Comparison Baseline):**
  - Architecture: `RandomForestClassifier`.
  - Hyperparameters: `n_estimators=100`, `max_depth=5`, `min_samples_leaf=3`, `class_weight="balanced"`, `random_state=42`.

### 4.5 Cross-Validation and Nested Evaluation Protocols
1. **Outer Resampling Protocol:** Repeated Stratified $K$-Fold Cross-Validation with $K = 5$ splits and $R = 5$ repeats, producing exactly **25 outer evaluation fold runs**. Random state is fixed at 42.
2. **Inner Calibration Protocol:** For calibrated targets (Cath, LAD, RCA), probability calibration is fit via `CalibratedClassifierCV(method="sigmoid", cv=3)` wrapped around the entire preprocessing-classifier pipeline. This implements a 3-fold inner cross-validation strictly inside each outer training fold.
3. **Threshold Selection Protocol:**
   - Standard Evaluation: Fixed arbitrary decision threshold $\tau = 0.50$.
   - Nested Inner-OOF Tuning: Within each outer training split, an inner 3-fold CV generates out-of-fold predictions; the threshold maximizing macro $F_1$ across candidate cutoffs $[0.05, 0.95]$ (step 0.01) is selected and applied to the outer test fold.
   - Fixed Operating Cutoffs: Production models deploy fixed cutoffs: $\tau = 0.50$ for Cath, LAD, and LCX; $\tau = 0.35$ for RCA (selected from the sigmoid-calibrated inner-OOF distribution mean 0.3188 ± 0.0380).

### 4.6 Explainability Framework and Calibration Disclosure
- **Attribution Engine:** Lundberg TreeSHAP (`shap.TreeExplainer` for XGBoost) and LinearSHAP (`shap.LinearExplainer` for Logistic Regression).
- **Background Baseline:** Computed using subsampled outer training partitions only (zero test data leakage).
- **Mathematical Space:**
  - TreeSHAP evaluates in raw log-odds margin space: $f(x) = \log \frac{p}{1-p}$.
  - LinearSHAP evaluates in decision function space: $f(x) = \mathbf{w}^T \mathbf{x} + b$.
- **Additivity Verification:** Additivity satisfies $\sum_{j=1}^M \phi_j(x) + \phi_0 = f(x)$. Verified on 100% of outer folds across all four targets within strict floating-point tolerance ($\le 1.19 \times 10^{-6}$ for XGBoost, $\le 1.78 \times 10^{-15}$ for Logistic Regression).
- **Calibration Disclosure:** SHAP values explain pre-calibration model scores $f(x)$. For Platt-calibrated models, final predicted probabilities undergo monotonic non-linear sigmoid transformation $P(Y=1|x) = \sigma(A f(x) + B)$. SHAP values cannot be linearly summed to reconstruct calibrated probabilities.

---

## 5. Master Evidence Matrix: Claim-by-Claim Traceability

| Claim ID | Scientific Claim / Finding | Exact Numerical Value(s) | Evaluation Protocol | Target | Authoritative Source File | Section / Code Location | Verification Status | Limitations & Boundary Qualifications |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | Total consecutive patients referred for coronary angiography | $N = 303$ | Retrospective cohort census | All | `data/reports/dataset_audit.json` | `quality_audit.n_rows` | Verified | Single-center (Tehran Heart Center); tertiary referral bias. |
| **CLM-02** | Complete data completeness across all audited features | 0 missing values (0.00%) | Complete dataset audit | All | `data/reports/dataset_audit.json` | `quality_audit.total_missing` | Verified | Natural zero missingness in audited Excel; imputation serves defensive role. |
| **CLM-03** | Overall CAD prevalence confirmed by catheterization | 71.29% ($N_+ = 216, N_- = 87$) | Cohort ground-truth tally | Cath | `data/reports/dataset_audit.json` | `targets_audit.Cath` | Verified | Reflects tertiary cardiology referral population; higher than general screening. |
| **CLM-04** | LAD obstructive stenosis prevalence ($\ge 50\%$) | 58.42% ($N_+ = 177, N_- = 126$) | Cohort ground-truth tally | LAD | `data/reports/dataset_audit.json` | `targets_audit.LAD` | Verified | Balanced target; supplies ~50% of left ventricular myocardium. |
| **CLM-05** | LCX obstructive stenosis prevalence ($\ge 50\%$) | 39.27% ($N_+ = 119, N_- = 184$) | Cohort ground-truth tally | LCX | `data/reports/dataset_audit.json` | `targets_audit.LCX` | Verified | Moderate class imbalance (1.55:1 negative-to-positive ratio). |
| **CLM-06** | RCA obstructive stenosis prevalence ($\ge 50\%$) | 37.62% ($N_+ = 114, N_- = 189$) | Cohort ground-truth tally | RCA | `data/reports/dataset_audit.json` | `targets_audit.RCA` | Verified | Moderate class imbalance (1.66:1 negative-to-positive ratio). |
| **CLM-07** | Target diagnostic coherence (Cath vs vessel stenosis) | 99.67% concordance (302/303) | Multi-target cross-tabulation | All | `data/reports/dataset_audit.md` | Section 2, Target Coherence | Verified | Exactly 1 discordant record (Index 93: isolated LAD stenosis with Cath='Normal'). |
| **CLM-08** | Number of active clinical predictive features | 54 features | Feature cleaner pipeline | All | `ml/preprocessing/pipeline.py` | `ClinicalFeatureCleaner` | Verified | Excludes 4 targets and 1 zero-variance column (`Exertional CP`). |
| **CLM-09** | Transformed numerical feature space dimensionality | 57 columns | One-Hot ColumnTransformer | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `schema_audit.transformed_feature_count` | Verified | Reflects One-Hot expansion of `VHD` (4 levels) and `BBB` (3 levels). |
| **CLM-10** | Primary discrimination: Cath XGBoost + Sigmoid | ROC-AUC: **$0.9123 \pm 0.0404$** (`ddof=1`)<br>[$0.0396$ with `ddof=0`]<br>PR-AUC: **$0.9597 \pm 0.0200$** (`ddof=1`)<br>[$0.0196$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | Cath | `data/reports/reproduction_audit/calibration_results.json` | `Cath.XGBoost_sigmoid.standard_threshold_metrics` | Verified | Internal repeated-CV folds are correlated; not an external validation. |
| **CLM-11** | Primary calibration reliability: Cath XGBoost + Sigmoid | Brier Score: **$0.1034 \pm 0.0251$** (`ddof=1`)<br>[$0.0246$ with `ddof=0`]<br>ECE: **$0.1004 \pm 0.0227$** (`ddof=1`)<br>[$0.0222$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | Cath | `data/reports/reproduction_audit/calibration_results.json` | `Cath.XGBoost_sigmoid.standard_threshold_metrics` | Verified | Platt scaling reduces Brier from 0.1074 to 0.1034 and ECE from 0.1265 to 0.1004. |
| **CLM-12** | Primary discrimination: LAD XGBoost + Sigmoid | ROC-AUC: **$0.8443 \pm 0.0528$** (`ddof=1`)<br>[$0.0518$ with `ddof=0`]<br>PR-AUC: **$0.8818 \pm 0.0471$** (`ddof=1`)<br>[$0.0462$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | LAD | `data/reports/reproduction_audit/calibration_results.json` | `LAD.XGBoost_sigmoid.standard_threshold_metrics` | Verified | RF baseline achieved $0.8528 \pm 0.0512$ ROC-AUC; delta $< 0.009$ within 1 SD. |
| **CLM-13** | Primary calibration reliability: LAD XGBoost + Sigmoid | Brier Score: **$0.1609 \pm 0.0226$** (`ddof=1`)<br>[$0.0221$ with `ddof=0`]<br>ECE: **$0.1326 \pm 0.0394$** (`ddof=1`)<br>[$0.0386$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | LAD | `data/reports/reproduction_audit/calibration_results.json` | `LAD.XGBoost_sigmoid.standard_threshold_metrics` | Verified | Superior calibration over RF (Brier 0.1674, ECE 0.1486) justifies XGBoost selection. |
| **CLM-14** | Primary discrimination: LCX XGBoost Uncalibrated | ROC-AUC: **$0.7358 \pm 0.0629$** (`ddof=1`)<br>[$0.0616$ with `ddof=0`]<br>PR-AUC: **$0.6173 \pm 0.0838$** (`ddof=1`)<br>[$0.0821$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | LCX | `data/reports/reproduction_audit/calibration_results.json` | `LCX.XGBoost_uncalibrated.standard_threshold_metrics` | Verified | Modest discrimination reflecting subtle posterolateral ischemia presentation. |
| **CLM-15** | Primary calibration reliability: LCX XGBoost Uncalibrated | Brier Score: **$0.2054 \pm 0.0240$** (`ddof=1`)<br>[$0.0235$ with `ddof=0`]<br>ECE: **$0.1366 \pm 0.0315$** (`ddof=1`)<br>[$0.0309$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | LCX | `data/reports/reproduction_audit/calibration_results.json` | `LCX.XGBoost_uncalibrated.standard_threshold_metrics` | Verified | Calibration post-processing collapsed minority sensitivity; uncalibrated retained. |
| **CLM-16** | Primary discrimination: RCA Logistic Regression + Sigmoid | ROC-AUC: **$0.7163 \pm 0.0605$** (`ddof=1`)<br>[$0.0593$ with `ddof=0`]<br>PR-AUC: **$0.6098 \pm 0.0775$** (`ddof=1`)<br>[$0.0759$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | RCA | `data/reports/reproduction_audit/calibration_results.json` | `RCA.LogisticRegression_sigmoid.standard_threshold_metrics` | Verified | Linear baseline matches RF ($0.7190 \pm 0.0555$) and exceeds XGBoost ($0.7036$). |
| **CLM-17** | Primary calibration reliability: RCA Logistic Regression + Sigmoid | Brier Score: **$0.2060 \pm 0.0150$** (`ddof=1`)<br>[$0.0147$ with `ddof=0`]<br>ECE: **$0.1000 \pm 0.0321$** (`ddof=1`)<br>[$0.0315$ with `ddof=0`] | 25-Fold Repeated-CV Outer Folds | RCA | `data/reports/reproduction_audit/calibration_results.json` | `RCA.LogisticRegression_sigmoid.standard_threshold_metrics` | Verified | Sigmoid calibration achieves lowest ECE (0.1000) and lowest Brier (0.2060). |
| **CLM-18** | Standard 0.50 cutoff classification performance: Cath | Acc: $0.8667 \pm 0.0411$<br>BalAcc: $0.8262 \pm 0.0513$<br>Sens: $0.9212 \pm 0.0361$<br>Spec: $0.7312 \pm 0.0855$<br>Prec: $0.8953 \pm 0.0318$<br>F1: $0.9077 \pm 0.0285$ | 25-Fold Repeated-CV Outer Folds at $\tau = 0.50$ (`ddof=1`) | Cath | `data/reports/reproduction_audit/calibration_results.json` | `Cath.XGBoost_sigmoid.standard_threshold_metrics` | Verified | Standard threshold aligns closely with inner-OOF tuned threshold mean (0.4912). |
| **CLM-19** | Standard 0.50 cutoff classification performance: LAD | Acc: $0.7868 \pm 0.0462$<br>BalAcc: $0.7730 \pm 0.0527$<br>Sens: $0.8568 \pm 0.0665$<br>Spec: $0.6891 \pm 0.1173$<br>Prec: $0.7995 \pm 0.0573$<br>F1: $0.8244 \pm 0.0372$ | 25-Fold Repeated-CV Outer Folds at $\tau = 0.50$ (`ddof=1`) | LAD | `data/reports/reproduction_audit/calibration_results.json` | `LAD.XGBoost_sigmoid.standard_threshold_metrics` | Verified | Balanced clinical sensitivity and specificity for primary coronary branch. |
| **CLM-20** | Standard 0.50 cutoff classification performance: LCX | Acc: $0.6871 \pm 0.0539$<br>BalAcc: $0.6744 \pm 0.0563$<br>Sens: $0.6163 \pm 0.0987$<br>Spec: $0.7325 \pm 0.0743$<br>Prec: $0.6020 \pm 0.0733$<br>F1: $0.6054 \pm 0.0744$ | 25-Fold Repeated-CV Outer Folds at $\tau = 0.50$ (`ddof=1`) | LCX | `data/reports/reproduction_audit/calibration_results.json` | `LCX.XGBoost_uncalibrated.standard_threshold_metrics` | Verified | Lower sensitivity reflects minority prevalence and diffuse clinical presentation. |
| **CLM-21** | Standard 0.50 cutoff probability compression failure: RCA | Acc: $0.6562 \pm 0.0504$<br>BalAcc: $0.5881 \pm 0.0500$<br>Sens: **$0.3124 \pm 0.0856$**<br>Spec: $0.8638 \pm 0.0741$<br>Prec: $0.5998 \pm 0.1346$<br>F1: **$0.4027 \pm 0.0872$** | 25-Fold Repeated-CV Outer Folds at $\tau = 0.50$ (`ddof=1`) | RCA | `data/reports/reproduction_audit/calibration_results.json` | `RCA.LogisticRegression_sigmoid.standard_threshold_metrics` | Verified | Proves severe clinical sensitivity collapse when using arbitrary 0.50 threshold on calibrated minority class. |
| **CLM-22** | Nested inner-OOF threshold selection distribution: RCA | Mean: $0.3188 \pm 0.0388$ (`ddof=1`)<br>[$0.0380$ with `ddof=0`]<br>Range: [0.2000, 0.3700] | Inner 3-fold CV inside 25 outer training folds | RCA | `data/reports/reproduction_audit/calibration_results.json` | `RCA.LogisticRegression_sigmoid.selected_thresholds` | Verified | Sigmoid calibration stabilizes threshold selection variance compared to uncalibrated LR ($0.3032 \pm 0.0774$). |
| **CLM-23** | Nested inner-OOF tuned classification performance: RCA | Acc: $0.6072 \pm 0.0716$<br>BalAcc: **$0.6443 \pm 0.0575$**<br>Sens: **$0.7946 \pm 0.1092$**<br>Spec: **$0.4941 \pm 0.1429$**<br>Prec: $0.4928 \pm 0.0532$<br>F1: **$0.6037 \pm 0.0516$** | 25-Fold Nested Inner-OOF Tuned Outer Evaluation (`ddof=1`) | RCA | `data/reports/reproduction_audit/calibration_results.json` | `RCA.LogisticRegression_sigmoid.tuned_threshold_metrics` | Verified | Evaluates outer test folds using each fold's inner-selected threshold; resolves sensitivity collapse. |
| **CLM-24A** | Fixed 0.35 threshold across 25 outer folds: RCA | Acc: $0.6377 \pm 0.0597$<br>BalAcc: $0.6585 \pm 0.0638$<br>Sens: $0.7421 \pm 0.1064$<br>Spec: $0.5748 \pm 0.0710$<br>Prec: $0.5139 \pm 0.0594$<br>F1: $0.6053 \pm 0.0684$ | 25 Outer Fold Evaluations at Fixed $\tau = 0.35$ (`ddof=1`) | RCA | Derived from stored `oof_y_prob` across 25 outer test folds | Verified | Evaluates fold-to-fold variability at fixed production cutoff $\tau = 0.35$. |
| **CLM-24B** | Five-repeat pooled evaluation at fixed 0.35: RCA | Acc: $0.6376 \pm 0.0075$<br>BalAcc: $0.6584 \pm 0.0102$<br>Sens: $0.7421 \pm 0.0253$<br>Spec: $0.5746 \pm 0.0110$<br>Prec: $0.5127 \pm 0.0067$<br>F1: $0.6063 \pm 0.0120$ | 5-Repeat Pooled Evaluation (Mean ± SD across $R=5$ repeats) | RCA | Evaluated on full $N=303$ cohort per repeat at $\tau = 0.35$ | Verified | Evaluates repeat-level stability over 5 independent complete cohort resamplings. |
| **CLM-25** | Mathematical verification of SHAP reconstruction additivity | 100% of folds passed<br>Max Diff Cath: $9.54 \times 10^{-7}$<br>Max Diff LAD: $9.54 \times 10^{-7}$<br>Max Diff LCX: $1.19 \times 10^{-6}$<br>Max Diff RCA: $1.78 \times 10^{-15}$ | Exact floating-point check: $\sum \phi_i + \phi_0 = f(x)$ | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.reconstruction_check` | Verified | Proves mathematical integrity of TreeSHAP and LinearSHAP in raw model-score space. |
| **CLM-26** | Global SHAP feature ranking stability across resampled folds | Spearman $\rho$:<br>Cath: $0.9319 \pm 0.0192$<br>LAD: $0.9217 \pm 0.0197$<br>LCX: $0.9081 \pm 0.0263$<br>RCA: $0.7737 \pm 0.0583$ | Pairwise Spearman rank correlation across 25 outer folds | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_a.global_stability.rank_correlation.spearman` | Verified | Tree-based models show high global rank stability ($\rho > 0.90$); RCA displays moderate stability due to linear collinearity. |
| **CLM-27** | Top-5 feature attribution consistency (Jaccard similarity) | Cath: $0.6887 \pm 0.1834$<br>LAD: $0.7456 \pm 0.1417$<br>LCX: $0.5195 \pm 0.1723$<br>RCA: $0.4890 \pm 0.1724$ | Pairwise Top-5 Jaccard index across 25 outer folds | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_a.global_stability.top_k_jaccard.top_5` | Verified | LAD displays highest Top-5 consistency driven by dominant anatomical anchors (`RWMA`, `EF-TTE`, `Age`). |
| **CLM-28** | Patient-level explanation sign agreement across 5 repeats | Cath: 91.09%<br>LAD: 90.03%<br>LCX: 86.72%<br>RCA: 86.07% | Proportion of consistent attribution signs per patient across 5 repeats | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_a.patient_level_stability.mean_sign_agreement` | Verified | Explanations agree on whether a feature is risk-elevating vs protective in $> 86\%$ of instances. |
| **CLM-29** | Empirical prediction dispersion across repeats (Mean $\sigma_p$) | Cath: $0.0385 \pm 0.0357$<br>LAD: $0.0488 \pm 0.0353$<br>LCX: $0.0701 \pm 0.0361$<br>RCA: $0.0404 \pm 0.0210$ | Across-patient standard deviation of predicted probability across 5 repeats | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_b.probability_stability` | Verified | Low probability dispersion across independent model fits indicates robust continuous estimation. |
| **CLM-30** | Proportion of patients with high probability dispersion ($\sigma_p > 0.10$) | Cath: 7.92% (24/303)<br>LAD: 11.22% (34/303)<br>LCX: 18.81% (57/303)<br>RCA: 1.98% (6/303) | Thresholded proportion of patients with $\sigma_p > 0.10$ | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_b.probability_stability.pct_sd_over_0_10` | Verified | RCA has the lowest high-dispersion rate due to linear regularizer stabilization. |
| **CLM-31** | Complete classification label invariance across 5 repeats | Cath: 91.09% (276/303)<br>LAD: 81.85% (248/303)<br>LCX: 67.00% (203/303)<br>RCA: 75.58% (229/303) | Proportion of patients with 5/5 identical binary classifications | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_b.classification_stability.pct_100_percent_consistent` | Verified | Invariance is strictly bounded by distance from the decision boundary. |
| **CLM-32** | Boundary proximity localization of classification flips | Distance $< 0.05$ from cutoff:<br>Cath: 0.0% perfect agreement ($N=6$)<br>LAD: 0.0% perfect agreement ($N=17$)<br>LCX: 2.2% perfect agreement ($N=45$)<br>RCA: 22.7% perfect agreement ($N=75$) | Stratification by $|p - \tau| < 0.05$ | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_b.classification_stability.threshold_proximity_stratification` | Verified | Flips are NOT randomly distributed across the cohort; they concentrate strictly at the cutoff boundary. |
| **CLM-33** | Confident prediction label invariance ($|p - \tau| \ge 0.20$) | Cath: 99.19% ($N=246$)<br>LAD: 100.0% ($N=190$)<br>LCX: 99.26% ($N=136$)<br>RCA: 100.0% ($N=48$) | Stratification by $|p - \tau| \ge 0.20$ | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_b.classification_stability.threshold_proximity_stratification` | Verified | Confident predictions achieve near-perfect classification invariance. |
| **CLM-34** | Predictive entropy discrimination for classification errors | Error-detection ROC-AUC:<br>Cath: 0.7593<br>LAD: 0.6595<br>LCX: 0.6392<br>RCA: 0.6796 | Binary entropy $H(p)$ ranking of empirical misclassifications | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_c.entropy_uncertainty.entropy_error_auc` | Verified | Normalized entropy acts as a defensive algorithmic flag; NOT a calibrated probability of error. |
| **CLM-35** | Margin-based classification error gradient | Error rate $< 0.05$ vs $\ge 0.20$:<br>Cath: 33.3% vs 1.6%<br>LAD: 41.2% vs 7.4%<br>LCX: 44.4% vs 14.7%<br>RCA: 40.0% vs 16.7% | Error frequency stratified by $|p - \tau|$ | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_c.margin_stratification` | Verified | Demonstrates consistent empirical inverse relationship between boundary distance and error occurrence. |
| **CLM-36** | Input perturbation robustness under moderate noise ($0.5\sigma$) | Label flip rate / mean prob shift:<br>Cath: 2.18% / 0.0201<br>LAD: 2.64% / 0.0210<br>LCX: 4.29% / 0.0348<br>RCA: 6.73% / 0.0254 | Additive Gaussian noise scaled to feature SD ($\epsilon \sim \mathcal{N}(0, (0.5\sigma)^2)$) | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_d.numerical_perturbation.feature_sensitivities` | Verified | Tree-based models demonstrate superior resistance to input noise compared to regularized linear models. |
| **CLM-37** | Synthetic missingness stress test degradation (10% MCAR) | Absolute ROC-AUC drop:<br>Cath: -0.0146 (0.9018 to 0.8872)<br>LAD: -0.0167 (0.8477 to 0.8310)<br>LCX: -0.0238 (0.7426 to 0.7188)<br>RCA: -0.0229 (0.7040 to 0.6811) | Synthetic MCAR evaluated against Repeat-1 5-fold pooled OOF baseline | All | `data/reports/phase4/robustness/{target}/{target}_robustness_summary.json` | `missingness_stress_test` | Verified | Pipeline's internal median imputer degrades smoothly under missingness up to 20%. |
| **CLM-38** | Echocardiographic feature block inside-CV ablation drop | Cath: $\Delta \text{AUC} = -0.0200$<br>LAD: $\Delta \text{AUC} = -0.0528$<br>LCX: $\Delta \text{AUC} = -0.0185$<br>RCA: $\Delta \text{AUC} = -0.0094$ | Retrained inside CV without `EF-TTE`, `Region RWMA`, `VHD` relative to Repeat-1 baseline | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_d.feature_ablation.ablations` | Verified | LAD displays profound dependence on echocardiography, reflecting anterior territorial wall motion changes. |
| **CLM-39** | Clinical symptoms & exam feature block inside-CV ablation drop | Cath: $\Delta \text{AUC} = -0.0847$<br>LAD: $\Delta \text{AUC} = -0.0532$<br>LCX: $\Delta \text{AUC} = -0.0124$<br>RCA: $\Delta \text{AUC} = -0.0280$ | Retrained inside CV without symptoms block relative to Repeat-1 baseline | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_d.feature_ablation.ablations` | Verified | Symptoms (primarily `Typical Chest Pain`) constitute the single largest marginal driver for Cath and LAD. |
| **CLM-40** | Laboratory panel feature block inside-CV ablation drop | Cath: $\Delta \text{AUC} = -0.0142$<br>LAD: $\Delta \text{AUC} = -0.0189$<br>LCX: $\Delta \text{AUC} = -0.0524$<br>RCA: $\Delta \text{AUC} = -0.0121$ | Retrained inside CV without lab features relative to Repeat-1 baseline | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_d.feature_ablation.ablations` | Verified | LCX depends predominantly on laboratory panels (`CR`, `TG`, `PLT`) due to absence of specific echocardiographic markers. |
| **CLM-41** | Subgroup feasibility qualification filtering | 13 strata qualified across 6 categories ($N \ge 30, \min(N_+, N_-) \ge 5$) | Sample size & class count feasibility guard | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_e.subgroup_feasibility_and_performance` | Verified | Guards prevent reporting unstable metrics on underpowered strata (e.g., CHF with only 1 positive case). |
| **CLM-42** | Sex subgroup descriptive performance parity | Cath ROC-AUC: Male 0.8779 vs Female 0.9495<br>LAD ROC-AUC: Male 0.8579 vs Female 0.8102<br>LCX ROC-AUC: Male 0.7557 vs Female 0.7482<br>RCA ROC-AUC: Male 0.6840 vs Female 0.7611 | Consensus patient OOF ($N=303$) evaluated by biological sex | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_e.subgroup_feasibility_and_performance.categories[0]` | Verified | Descriptive stratification only; does NOT constitute formal algorithmic fairness certification. |
| **CLM-43** | Older age stratum descriptive discrimination attenuation | Cath ROC-AUC: $<55$: 0.8954; $55-65$: 0.9534; $\ge 65$: 0.7480<br>LAD ROC-AUC: $<55$: 0.8569; $55-65$: 0.8451; $\ge 65$: 0.7171 | Consensus patient OOF ($N=303$) evaluated by age stratum | All | `data/reports/phase4/summary/phase4_master_metrics.json` | `target_results.{target}.exp_e.subgroup_feasibility_and_performance.categories[1]` | Verified | Descriptive observation in $N=95$ older patients; hypothesis-generating only, mechanisms unestablished. |

---

## 6. Locked Scientific Results Tables

### Table 1: Clinical Cohort Baseline Characteristics & Target Distributions
*Authoritative Source: `data/reports/dataset_audit.json` and `data/reports/dataset_audit.md`.*

| Characteristic / Variable | Entire Cohort ($N = 303$) | Cath Positive ($N = 216$) | Cath Negative ($N = 87$) | Missing Count (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Age (years), Mean ± SD [Median, IQR]** | $58.89 \pm 10.39$ [$60.0, 15.0$] | $60.52 \pm 9.87$ [$61.0, 14.0$] | $54.85 \pm 10.51$ [$55.0, 15.0$] | 0 (0.00%) |
| **Sex, Male / Female (% Male)** | 176 / 127 (58.09%) | 130 / 86 (60.19%) | 46 / 41 (52.87%) | 0 (0.00%) |
| **Body Mass Index (BMI, kg/m²), Mean ± SD** | $27.02 \pm 4.09$ [$26.78, 4.90$] | $26.89 \pm 3.98$ | $27.34 \pm 4.36$ | 0 (0.00%) |
| **Systolic Blood Pressure (BP, mmHg), Median [IQR]** | 130.0 [20.0] | 130.0 [20.0] | 120.0 [20.0] | 0 (0.00%) |
| **Ejection Fraction (EF-TTE, %), Median [IQR]** | 50.0 [10.0] | 45.0 [15.0] | 50.0 [5.0] | 0 (0.00%) |
| **Fasting Blood Sugar (FBS, mg/dL), Median [IQR]** | 98.0 [41.5] | 104.0 [54.0] | 92.0 [21.5] | 0 (0.00%) |
| **Serum Triglycerides (TG, mg/dL), Median [IQR]** | 122.0 [87.0] | 133.0 [97.5] | 108.0 [66.5] | 0 (0.00%) |
| **Typical Chest Pain Presentation, Count (%)** | 164 (54.13%) | 148 (68.52%) | 16 (18.39%) | 0 (0.00%) |
| **Regional Wall Motion Abnormality (RWMA), Count (%)** | 68 (22.44%) | 65 (30.09%) | 3 (3.45%) | 0 (0.00%) |
| **Diabetes Mellitus (DM), Count (%)** | 90 (29.70%) | 78 (36.11%) | 12 (13.79%) | 0 (0.00%) |
| **Hypertension (HTN), Count (%)** | 179 (59.08%) | 136 (62.96%) | 43 (49.43%) | 0 (0.00%) |
| **Target: Cath Obstructive CAD (Any Vessel $\ge 50\%$)** | 216 (71.29%) | 216 (100.0%) | 0 (0.00%) | 0 (0.00%) |
| **Target: LAD Stenosis ($\ge 50\%$)** | 177 (58.42%) | 176 (81.48%) | 1 (1.15%)* | 0 (0.00%) |
| **Target: LCX Stenosis ($\ge 50\%$)** | 119 (39.27%) | 119 (55.09%) | 0 (0.00%) | 0 (0.00%) |
| **Target: RCA Stenosis ($\ge 50\%$)** | 114 (37.62%) | 114 (52.78%) | 0 (0.00%) | 0 (0.00%) |

*\*Note on Record Index 93: Patient exhibits LAD='Stenotic', LCX='Normal', RCA='Normal', Cath='Normal'. Preserved without alteration.*

---

### Table 2: Benchmark Multi-Target Discrimination & Calibration Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json` and `data/reports/reproduction_audit/model_benchmark.json`.*  
*Protocol: Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats = 25 outer folds). Primary metrics report Cross-Fold Mean $\pm$ Sample SD (`ddof=1`, $N=24$), with population SD (`ddof=0`, $N=25$) noted in brackets.*

| Target | Clinical Endpoint | Selected Model | Scaling & Preprocessing | Calibration Method | Operating Cutoff | ROC-AUC (Mean $\pm$ SD) | PR-AUC (Mean $\pm$ SD) | Brier Score (Mean $\pm$ SD) | ECE (Mean $\pm$ SD) |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Cath** | Overall CAD Status | **XGBoost** | None, One-Hot | **Sigmoid** (Platt) | 0.50 | **$0.9123 \pm 0.0404$**<br>[$0.0396$ with `ddof=0`] | **$0.9597 \pm 0.0200$**<br>[$0.0196$ with `ddof=0`] | **$0.1034 \pm 0.0251$**<br>[$0.0246$ with `ddof=0`] | **$0.1004 \pm 0.0227$**<br>[$0.0222$ with `ddof=0`] |
| **LAD** | Left Anterior Descending | **XGBoost** | None, One-Hot | **Sigmoid** (Platt) | 0.50 | **$0.8443 \pm 0.0528$**<br>[$0.0518$ with `ddof=0`] | **$0.8818 \pm 0.0471$**<br>[$0.0462$ with `ddof=0`] | **$0.1609 \pm 0.0226$**<br>[$0.0221$ with `ddof=0`] | **$0.1326 \pm 0.0394$**<br>[$0.0386$ with `ddof=0`] |
| **LCX** | Left Circumflex | **XGBoost** | None, One-Hot | **Uncalibrated** | 0.50 | **$0.7358 \pm 0.0629$**<br>[$0.0616$ with `ddof=0`] | **$0.6173 \pm 0.0838$**<br>[$0.0821$ with `ddof=0`] | **$0.2054 \pm 0.0240$**<br>[$0.0235$ with `ddof=0`] | **$0.1366 \pm 0.0315$**<br>[$0.0309$ with `ddof=0`] |
| **RCA** | Right Coronary Artery | **Logistic Regression** | StandardScaler, One-Hot | **Sigmoid** (Platt) | 0.35 | **$0.7163 \pm 0.0605$**<br>[$0.0593$ with `ddof=0`] | **$0.6098 \pm 0.0775$**<br>[$0.0759$ with `ddof=0`] | **$0.2060 \pm 0.0150$**<br>[$0.0147$ with `ddof=0`] | **$0.1000 \pm 0.0321$**<br>[$0.0315$ with `ddof=0`] |

---

### Table 3: Calibration Method Comparison Across Model Architectures
*Authoritative Source: `data/reports/reproduction_audit/model_benchmark.json`.*  
*Protocol: 25-fold outer repeated-CV fold distributions (Mean $\pm$ Sample SD, `ddof=1`).*

| Target | Model Candidate | Calibration Method | Brier Score (Lower is Better) | ECE (Lower is Better) | ROC-AUC (Mean $\pm$ SD) | Selected Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Cath** | Logistic Regression | Uncalibrated | $0.1156 \pm 0.0307$ | $0.1200 \pm 0.0294$ | $0.9156 \pm 0.0361$ | Baseline |
| | Logistic Regression | Sigmoid (Platt) | $0.1070 \pm 0.0202$ | $0.1082 \pm 0.0270$ | $0.9176 \pm 0.0354$ | Candidate |
| | Logistic Regression | Isotonic | $0.1089 \pm 0.0255$ | $0.1001 \pm 0.0241$ | $0.9131 \pm 0.0363$ | Candidate |
| | XGBoost | Uncalibrated | $0.1074 \pm 0.0256$ | $0.1265 \pm 0.0218$ | $0.9125 \pm 0.0389$ | Candidate |
| | **XGBoost** | **Sigmoid (Platt)** | **$0.1034 \pm 0.0251$** | **$0.1004 \pm 0.0227$** | **$0.9123 \pm 0.0404$** | **Selected Production** |
| | XGBoost | Isotonic | $0.1044 \pm 0.0283$ | $0.1068 \pm 0.0256$ | $0.9124 \pm 0.0420$ | Candidate |
| **LAD** | Logistic Regression | Uncalibrated | $0.1849 \pm 0.0335$ | $0.1477 \pm 0.0449$ | $0.8171 \pm 0.0538$ | Baseline |
| | Logistic Regression | Sigmoid (Platt) | $0.1740 \pm 0.0188$ | $0.1306 \pm 0.0405$ | $0.8207 \pm 0.0507$ | Candidate |
| | Logistic Regression | Isotonic | $0.1726 \pm 0.0230$ | $0.1426 \pm 0.0298$ | $0.8179 \pm 0.0492$ | Candidate |
| | XGBoost | Uncalibrated | $0.1651 \pm 0.0257$ | $0.1434 \pm 0.0331$ | $0.8338 \pm 0.0530$ | Candidate |
| | **XGBoost** | **Sigmoid (Platt)** | **$0.1609 \pm 0.0226$** | **$0.1326 \pm 0.0394$** | **$0.8443 \pm 0.0528$** | **Selected Production** |
| | XGBoost | Isotonic | $0.1623 \pm 0.0260$ | $0.1339 \pm 0.0318$ | $0.8396 \pm 0.0517$ | Candidate |
| **LCX** | Logistic Regression | Uncalibrated | $0.2393 \pm 0.0367$ | $0.1827 \pm 0.0514$ | $0.6850 \pm 0.0768$ | Baseline |
| | Logistic Regression | Sigmoid (Platt) | $0.2171 \pm 0.0168$ | $0.1050 \pm 0.0453$ | $0.6896 \pm 0.0766$ | Candidate |
| | Logistic Regression | Isotonic | $0.2192 \pm 0.0242$ | $0.1287 \pm 0.0436$ | $0.6838 \pm 0.0794$ | Candidate |
| | **XGBoost** | **Uncalibrated** | **$0.2054 \pm 0.0240$** | **$0.1366 \pm 0.0315$** | **$0.7358 \pm 0.0629$** | **Selected Production** |
| | XGBoost | Sigmoid (Platt) | $0.2073 \pm 0.0155$ | $0.1068 \pm 0.0302$ | $0.7254 \pm 0.0582$ | Candidate |
| | XGBoost | Isotonic | $0.2078 \pm 0.0190$ | $0.1299 \pm 0.0389$ | $0.7296 \pm 0.0533$ | Candidate |
| **RCA** | Logistic Regression | Uncalibrated | $0.2245 \pm 0.0278$ | $0.1673 \pm 0.0373$ | $0.7160 \pm 0.0614$ | Baseline |
| | **Logistic Regression** | **Sigmoid (Platt)** | **$0.2060 \pm 0.0150$** | **$0.1000 \pm 0.0321$** | **$0.7163 \pm 0.0605$** | **Selected Production** |
| | Logistic Regression | Isotonic | $0.2069 \pm 0.0188$ | $0.1236 \pm 0.0423$ | $0.7134 \pm 0.0601$ | Candidate |
| | XGBoost | Uncalibrated | $0.2154 \pm 0.0236$ | $0.1490 \pm 0.0304$ | $0.7036 \pm 0.0634$ | Candidate |
| | XGBoost | Sigmoid (Platt) | $0.2092 \pm 0.0125$ | $0.1146 \pm 0.0350$ | $0.7080 \pm 0.0554$ | Candidate |
| | XGBoost | Isotonic | $0.2090 \pm 0.0145$ | $0.1148 \pm 0.0432$ | $0.7083 \pm 0.0558$ | Candidate |

---

### Table 4: Standard Threshold (0.50) Binary Classification Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json`.*  
*Protocol: 25 outer fold evaluations at fixed decision cutoff $\tau = 0.50$ (Mean $\pm$ Sample SD, `ddof=1`).*

| Target | Selected Model & Calibration | Accuracy (Mean $\pm$ SD) | Balanced Accuracy (Mean $\pm$ SD) | Sensitivity / Recall (Mean $\pm$ SD) | Specificity (Mean $\pm$ SD) | Precision (Mean $\pm$ SD) | $F_1$-Score (Mean $\pm$ SD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | XGBoost + Sigmoid | $0.8667 \pm 0.0411$ | $0.8262 \pm 0.0513$ | $0.9212 \pm 0.0361$ | $0.7312 \pm 0.0855$ | $0.8953 \pm 0.0318$ | $0.9077 \pm 0.0285$ |
| **LAD** | XGBoost + Sigmoid | $0.7868 \pm 0.0462$ | $0.7730 \pm 0.0527$ | $0.8568 \pm 0.0665$ | $0.6891 \pm 0.1173$ | $0.7995 \pm 0.0573$ | $0.8244 \pm 0.0372$ |
| **LCX** | XGBoost Uncalibrated | $0.6871 \pm 0.0539$ | $0.6744 \pm 0.0563$ | $0.6163 \pm 0.0987$ | $0.7325 \pm 0.0743$ | $0.6020 \pm 0.0733$ | $0.6054 \pm 0.0744$ |
| **RCA** | Logistic Regression + Sigmoid | $0.6562 \pm 0.0504$ | $0.5881 \pm 0.0500$ | **$0.3124 \pm 0.0856$** | $0.8638 \pm 0.0741$ | $0.5998 \pm 0.1346$ | **$0.4027 \pm 0.0872$** |

---

### Table 5: Nested Inner-Fold Threshold Tuning Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json`.*  
*Protocol: 25 outer fold evaluations where decision threshold is tuned strictly on inner 3-fold OOF training predictions to maximize macro $F_1$ (Mean $\pm$ Sample SD, `ddof=1`).*

| Target | Selected Model & Calibration | Selected Threshold Distribution (Mean $\pm$ SD [Min, Max]) | Accuracy (Mean $\pm$ SD) | Balanced Accuracy (Mean $\pm$ SD) | Sensitivity / Recall (Mean $\pm$ SD) | Specificity (Mean $\pm$ SD) | Precision (Mean $\pm$ SD) | $F_1$-Score (Mean $\pm$ SD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | XGBoost + Sigmoid | $0.4912 \pm 0.0760$ [$0.34, 0.63$] | $0.8686 \pm 0.0392$ | $0.8269 \pm 0.0521$ | $0.9249 \pm 0.0387$ | $0.7289 \pm 0.0971$ | $0.8954 \pm 0.0347$ | $0.9093 \pm 0.0270$ |
| **LAD** | XGBoost + Sigmoid | $0.4496 \pm 0.0580$ [$0.32, 0.54$] | $0.7815 \pm 0.0564$ | $0.7629 \pm 0.0673$ | $0.8760 \pm 0.0652$ | $0.6497 \pm 0.1528$ | $0.7855 \pm 0.0686$ | $0.8248 \pm 0.0407$ |
| **LCX** | XGBoost Uncalibrated | $0.3452 \pm 0.0773$ [$0.16, 0.43$] | $0.6205 \pm 0.0714$ | $0.6508 \pm 0.0648$ | $0.7944 \pm 0.1201$ | $0.5072 \pm 0.1348$ | $0.5161 \pm 0.0638$ | $0.6215 \pm 0.0646$ |
| **RCA** | Logistic Regression + Sigmoid | $0.3188 \pm 0.0388$ [$0.20, 0.37$] | $0.6072 \pm 0.0716$ | **$0.6443 \pm 0.0575$** | **$0.7946 \pm 0.1092$** | **$0.4941 \pm 0.1429$** | $0.4928 \pm 0.0532$ | **$0.6037 \pm 0.0516$** |

---

### Table 6: Production Operating Threshold Performance & Protocol Separation (RCA Deep Dive)
*Authoritative Source: `models/rca/metadata.json`, `data/reports/reproduction_audit/calibration_results.json`, and stored `oof_y_prob`.*

> **Critical Protocol Separation Mandate:**  
> The evaluation of RCA must strictly segregate four distinct evaluation protocols. Never describe the 5-repeat mean ± SD as the 25-fold mean ± SD.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         RCA EVALUATION PROTOCOL SEPARATION MATRIX                                      │
├────────────────────────────────┬──────────────┬──────────────┬───────────────────┬─────────────────────────────────────┤
│ Protocol Description           │ Sample Unit  │ Sample Count │ Cutoff Rule       │ Metrics (Recall / F1 / BalAcc)      │
├────────────────────────────────┼──────────────┼──────────────┼───────────────────┼─────────────────────────────────────┤
│ 1. Standard 0.50 (25-Fold)     │ Outer Fold   │ 25 folds     │ Fixed tau = 0.50  │ Sens: 0.312 ± 0.086, F1: 0.403 ± 0.087│
│ 2. Nested Tuned (25-Fold)      │ Outer Fold   │ 25 folds     │ Inner-OOF dynamic │ Sens: 0.795 ± 0.109, F1: 0.604 ± 0.052│
│ 3. Fixed 0.35 (25-Fold)        │ Outer Fold   │ 25 folds     │ Fixed tau = 0.35  │ Sens: 0.742 ± 0.106, F1: 0.605 ± 0.068│
│ 4. Fixed 0.35 (5-Repeat Pooled)│ CV Repeat    │ 5 repeats    │ Fixed tau = 0.35  │ Sens: 0.742 ± 0.025, F1: 0.606 ± 0.012│
└────────────────────────────────┴──────────────┴──────────────┴───────────────────┴─────────────────────────────────────┘
```

#### Detailed Breakdown of Protocols for RCA (`LogisticRegression_sigmoid`):

1. **Protocol 1: Standard Arbitrary Cutoff ($\tau = 0.50$) across 25 Outer Folds:**
   - Evaluated on each of the 25 outer test folds at fixed cutoff $\tau = 0.50$.
   - **Metrics (Mean $\pm$ Sample SD, `ddof=1`):** Accuracy $0.6562 \pm 0.0504$, Balanced Accuracy $0.5881 \pm 0.0500$, Sensitivity $0.3124 \pm 0.0856$, Specificity $0.8638 \pm 0.0741$, Precision $0.5998 \pm 0.1346$, $F_1$-Score $0.4027 \pm 0.0872$.
   - *Clinical Significance:* Demonstrates catastrophic sensitivity collapse ($31.2\%$) caused by Platt probability compression on this minority target (prevalence 37.6%).

2. **Protocol 2: Nested Inner-OOF Tuned Cutoff across 25 Outer Folds:**
   - On each outer training partition, an inner 3-fold CV determines the cutoff maximizing macro $F_1$ across $[0.05, 0.95]$ (selected cutoff distribution: Mean $0.3188 \pm 0.0388$, range $[0.20, 0.37]$). That cutoff is then applied to the untouched outer test fold.
   - **Metrics (Mean $\pm$ Sample SD, `ddof=1`):** Accuracy $0.6072 \pm 0.0716$, Balanced Accuracy $0.6443 \pm 0.0575$, Sensitivity $0.7946 \pm 0.1092$, Specificity $0.4941 \pm 0.1429$, Precision $0.4928 \pm 0.0532$, $F_1$-Score $0.6037 \pm 0.0516$.
   - *Source Artifact Note:* These are the exact numbers serialized into `models/rca/metadata.json` under `cv_metrics`.

3. **Protocol 3: Fixed Production Cutoff ($\tau = 0.35$) across 25 Outer Folds:**
   - Evaluated on each of the 25 outer test folds at the fixed production operating cutoff $\tau = 0.35$ (derived by rounding within 1 SD of the inner-OOF distribution mean: $0.3188 + 0.0388 = 0.3576$).
   - **Metrics (Mean $\pm$ Sample SD across 25 folds, `ddof=1`):** Accuracy $0.6377 \pm 0.0597$, Balanced Accuracy $0.6585 \pm 0.0638$, Sensitivity $0.7421 \pm 0.1064$, Specificity $0.5748 \pm 0.0710$, Precision $0.5139 \pm 0.0594$, $F_1$-Score $0.6053 \pm 0.0684$.

4. **Protocol 4: Fixed Production Cutoff ($\tau = 0.35$) across Five Repeated CV Runs:**
   - Out-of-fold predictions for all $N = 303$ patients are collected per repeat $r \in \{1, \dots, 5\}$. Metrics are calculated for each complete cohort repeat, and aggregated as the Mean $\pm$ Sample SD across the 5 repeats ($N=5, \text{ddof}=1$).
   - **Metrics (Mean $\pm$ Sample SD across 5 repeats):** Accuracy $0.6376 \pm 0.0075$, Balanced Accuracy $0.6584 \pm 0.0102$, Sensitivity $0.7421 \pm 0.0253$, Specificity $0.5746 \pm 0.0110$, Precision $0.5127 \pm 0.0067$, $F_1$-Score $0.6063 \pm 0.0120$.
   - *Aggregation Rule:* Standard deviation describes repeat-to-repeat variance across complete cohort resampling, yielding a tighter spread ($\pm 0.0253$ vs $\pm 0.1064$) than the 25-fold outer evaluation because each repeat contains the full $N=303$ cohort.

---

### Table 7: SHAP Explanation Stability Across Resampled Cross-Validation Folds
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp A).*  
*Protocol: 25 outer folds (5 splits $\times$ 5 repeats). Pairwise global correlations across 300 fold pairs. Patient-level stability evaluated across 5 independent out-of-fold explanations per patient ($N=303$).*

| Metric Dimension | Cath (XGBoost) | LAD (XGBoost) | LCX (XGBoost) | RCA (Logistic Regression) |
| :--- | :---: | :---: | :---: | :---: |
| **Explanation Mathematical Space** | Margin / Log-Odds ($f(x)$) | Margin / Log-Odds ($f(x)$) | Margin / Log-Odds ($f(x)$) | Decision Function ($f(x)$) |
| **Reconstruction Additivity Pass Rate** | **100.0% (25/25)** | **100.0% (25/25)** | **100.0% (25/25)** | **100.0% (25/25)** |
| **Max Reconstruction Error** | $9.54 \times 10^{-7}$ | $9.54 \times 10^{-7}$ | $1.19 \times 10^{-6}$ | $1.78 \times 10^{-15}$ |
| **Global Spearman Rank Correlation ($\rho \pm \text{SD}$)** | **$0.9319 \pm 0.0192$** | **$0.9217 \pm 0.0197$** | **$0.9081 \pm 0.0263$** | **$0.7737 \pm 0.0583$** |
| **Global Spearman Range [Min, Max]** | [0.8644, 0.9738] | [0.8414, 0.9633] | [0.8152, 0.9679] | [0.5690, 0.8912] |
| **Global Kendall’s Tau ($\tau \pm \text{SD}$)** | $0.8133 \pm 0.0293$ | $0.7893 \pm 0.0326$ | $0.7828 \pm 0.0363$ | $0.6011 \pm 0.0568$ |
| **Top-5 Feature Jaccard Similarity** | $0.6887 \pm 0.1834$ | **$0.7456 \pm 0.1417$** | $0.5195 \pm 0.1723$ | $0.4890 \pm 0.1724$ |
| **Top-10 Feature Jaccard Similarity** | $0.7475 \pm 0.1254$ | $0.5354 \pm 0.1190$ | $0.6060 \pm 0.1084$ | $0.5685 \pm 0.1126$ |
| **Patient Attribution Sign Agreement (%)** | **91.09%** | **90.03%** | **86.72%** | **86.07%** |
| **Patient Mean Rank Correlation** | 0.7717 | 0.7661 | 0.6823 | 0.7382 |
| **Top-5 Features by Inclusion Frequency** | `Age` (100%), `Typical Chest Pain` (100%), `EF-TTE` (92%), `Region RWMA` (88%), `FBS` (44%) | `Age` (100%), `EF-TTE` (100%), `Region RWMA` (100%), `Typical Chest Pain` (100%), `ESR` (48%) | `Age` (100%), `Typical Chest Pain` (100%), `CR` (72%), `TG` (60%), `PLT` (60%) | `Age` (100%), `DM` (96%), `Function Class` (64%), `Dyspnea` (60%), `ESR` (52%) |

---

### Table 8: Prediction Stability and Boundary Proximity Stratification
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp B).*  
*Protocol: 5 repeats of 5-fold CV yielding 5 independent out-of-fold probability estimates per patient ($N=303$).*

| Prediction Metric Dimension | Cath | LAD | LCX | RCA |
| :--- | :---: | :---: | :---: | :---: |
| **Operating Decision Cutoff ($\tau$)** | 0.50 | 0.50 | 0.50 | 0.35 |
| **Across-Patient Mean Probability SD ($\sigma_p$)** | **0.0385** | **0.0488** | **0.0701** | **0.0404** |
| **Across-Patient Median Probability SD** | 0.0248 | 0.0450 | 0.0675 | 0.0370 |
| **Maximum Observed Patient SD ($\max \sigma_p$)** | 0.1733 | 0.1622 | 0.1736 | 0.1286 |
| **Proportion with High Dispersion ($\sigma_p > 0.05$)** | 27.39% (83/303) | 41.58% (126/303) | 71.95% (218/303) | 27.39% (83/303) |
| **Proportion with Severe Dispersion ($\sigma_p > 0.10$)** | 7.92% (24/303) | 11.22% (34/303) | 18.81% (57/303) | 1.98% (6/303) |
| **Patient Risk Ranking Spearman Correlation** | 0.9221 | 0.9339 | 0.8604 | 0.8975 |
| **100% Invariant Labels (5/5 Identical Classifications)** | **91.09% (276/303)** | **81.85% (248/303)** | **67.00% (203/303)** | **75.58% (229/303)** |
| **$\ge 80\%$ Classification Agreement ($\ge 4/5$ Identical)** | 98.02% (297/303) | 93.07% (282/303) | 86.14% (261/303) | 87.79% (266/303) |

#### Boundary Proximity Stratification Matrix ($|p - \tau|$)

| Target | Distance to Cutoff ($|p - \tau|$) | Patient Count ($N$) | Proportion of Cohort (%) | 100% Invariant Labels (%) | Mean Label Agreement (%) | Mean Prob SD ($\sigma_p$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Cath** | Borderline ($< 0.05$) | 6 | 1.98% | **0.0%** | 63.33% | 0.1027 |
| | Near ($0.05 - 0.10$) | 14 | 4.62% | 28.57% | 84.29% | 0.0911 |
| | Moderate ($0.10 - 0.20$) | 37 | 12.21% | 75.68% | 95.14% | 0.0797 |
| | Confident ($\ge 0.20$) | 246 | 81.19% | **99.19%** | 99.84% | 0.0277 |
| **LAD** | Borderline ($< 0.05$) | 17 | 5.61% | **0.0%** | 64.71% | 0.0707 |
| | Near ($0.05 - 0.10$) | 34 | 11.22% | 29.41% | 81.18% | 0.0706 |
| | Moderate ($0.10 - 0.20$) | 62 | 20.46% | 77.42% | 95.48% | 0.0731 |
| | Confident ($\ge 0.20$) | 190 | 62.71% | **100.0%** | 100.0% | 0.0351 |
| **LCX** | Borderline ($< 0.05$) | 45 | 14.85% | **2.22%** | 67.11% | 0.0959 |
| | Near ($0.05 - 0.10$) | 38 | 12.54% | 31.58% | 80.53% | 0.0828 |
| | Moderate ($0.10 - 0.20$) | 84 | 27.72% | 65.48% | 92.86% | 0.0837 |
| | Confident ($\ge 0.20$) | 136 | 44.88% | **99.26%** | 99.85% | 0.0496 |
| **RCA** | Borderline ($< 0.05$) | 75 | 24.75% | **22.67%** | 74.67% | 0.0376 |
| | Near ($0.05 - 0.10$) | 68 | 22.44% | 82.35% | 96.47% | 0.0367 |
| | Moderate ($0.10 - 0.20$) | 112 | 36.96% | 96.43% | 99.29% | 0.0434 |
| | Confident ($\ge 0.20$) | 48 | 15.84% | **100.0%** | 100.0% | 0.0429 |

---

### Table 9: Predictive Uncertainty & Empirical Error Discrimination
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp C).*  
*Protocol: Normalized binary entropy $H(p) = -p \log_2(p) - (1-p) \log_2(1-p)$ and margin $|p - \tau|$ evaluated on consensus out-of-fold predictions ($N=303$).*

| Uncertainty Metric | Cath | LAD | LCX | RCA |
| :--- | :---: | :---: | :---: | :---: |
| **Error Detection Discrimination (Entropy $H(p)$ ROC-AUC)** | **0.7593** | **0.6595** | **0.6392** | **0.6796** |
| **Correct Detection Discrimination (Margin $|p - \tau|$ ROC-AUC)** | **0.7593** | **0.6595** | **0.6392** | **0.5602** |
| **Mean Predictive Entropy: Correct Classifications** | 0.5458 | 0.7650 | 0.8094 | 0.8651 |
| **Mean Predictive Entropy: Misclassified Patients** | 0.7795 | 0.8535 | 0.8934 | 0.9389 |
| **Entropy Difference ($\Delta H$)** | **+0.2337** | **+0.0885** | **+0.0840** | **+0.0738** |
| **Empirical Misclassification Rate: Margin $< 0.05$** | 33.33% (2/6) | 41.18% (7/17) | 44.44% (20/45) | 40.00% (30/75) |
| **Empirical Misclassification Rate: Margin $0.05 - 0.10$** | 21.43% (3/14) | 32.35% (11/34) | 42.11% (16/38) | 38.24% (26/68) |
| **Empirical Misclassification Rate: Margin $0.10 - 0.20$** | 16.22% (6/37) | 27.42% (17/62) | 23.81% (20/84) | 26.79% (30/112) |
| **Empirical Misclassification Rate: Margin $\ge 0.20$** | **1.63% (4/246)** | **7.37% (14/190)** | **14.71% (20/136)** | **16.67% (8/48)** |

---

### Table 10: Model Robustness Under Input Perturbations and Synthetic Missingness
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp D).*

#### Part A: Gaussian Physiological Input Perturbation ($\epsilon \sim \mathcal{N}(0, (\alpha \cdot \text{std})^2)$)

| Target | Noise Scale ($\alpha$) | Mean Absolute Probability Shift ($\Delta p$) | Overall Classification Flip Rate (%) | Most Sensitive Predictors (Highest $\Delta p$) |
| :--- | :---: | :---: | :---: | :--- |
| **Cath** | $0.1\sigma$ | 0.0039 | 0.46% | `Age` (0.0039), `TG` (0.0047), `EF-TTE` (0.0035) |
| | $0.5\sigma$ | 0.0201 | 2.18% | `Age` (0.0201), `TG` (0.0201), `EF-TTE` (0.0152) |
| | $1.0\sigma$ | 0.0396 | 4.36% | `Age` (0.0396), `TG` (0.0339), `EF-TTE` (0.0285) |
| **LAD** | $0.1\sigma$ | 0.0041 | 0.53% | `EF-TTE` (0.0041), `Age` (0.0037), `ESR` (0.0026) |
| | $0.5\sigma$ | 0.0210 | 2.64% | `EF-TTE` (0.0210), `Age` (0.0182), `ESR` (0.0128) |
| | $1.0\sigma$ | 0.0398 | 5.41% | `EF-TTE` (0.0398), `Age` (0.0343), `ESR` (0.0240) |
| **LCX** | $0.1\sigma$ | 0.0075 | 0.92% | `Age` (0.0075), `TG` (0.0062), `PLT` (0.0049) |
| | $0.5\sigma$ | 0.0348 | 4.29% | `Age` (0.0348), `TG` (0.0298), `PLT` (0.0232) |
| | $1.0\sigma$ | 0.0649 | 7.00% | `Age` (0.0649), `TG` (0.0549), `PLT` (0.0441) |
| **RCA** | $0.1\sigma$ | 0.0051 | 1.32% | `Age` (0.0051), `ESR` (0.0038), `TG` (0.0034) |
| | $0.5\sigma$ | 0.0254 | 6.73% | `Age` (0.0254), `ESR` (0.0188), `TG` (0.0169) |
| | $1.0\sigma$ | 0.0508 | 13.40% | `Age` (0.0508), `ESR` (0.0374), `TG` (0.0333) |

#### Part B: Synthetic Missingness Stress Testing (MCAR)
*Baseline: Repeat-1 5-fold CV pooled OOF sample ($N=303$).*

| Target | Baseline ROC-AUC (0% Missing) | 5% MCAR Missingness | 10% MCAR Missingness | 20% MCAR Missingness | Net ROC-AUC Drop at 20% MCAR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cath** | 0.9018 | 0.8945 | 0.8872 | 0.8654 | -0.0364 |
| **LAD** | 0.8477 | 0.8398 | 0.8310 | 0.8105 | -0.0372 |
| **LCX** | 0.7426 | 0.7305 | 0.7188 | 0.6901 | -0.0525 |
| **RCA** | 0.7040 | 0.6924 | 0.6811 | 0.6540 | -0.0500 |

---

### Table 11: Inside-CV Feature Group and Single-Feature Ablation
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp D).*  
*Protocol: Models retrained across 5-fold CV with specified features excluded inside the pipeline. Reference baseline: Repeat-1 unablated model.*

| Ablated Feature Group / Single Feature | Features Removed Count | Cath ($\Delta \text{ROC-AUC}$) | LAD ($\Delta \text{ROC-AUC}$) | LCX ($\Delta \text{ROC-AUC}$) | RCA ($\Delta \text{ROC-AUC}$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Repeat-1 Unablated Baseline ROC-AUC** | 0 | **0.9018** | **0.8477** | **0.7426** | **0.7040** |
| **Symptoms & Physical Examination** | 13 | **-0.0847** | **-0.0532** | -0.0124 | **-0.0280** |
| **Echocardiography (`EF-TTE`, `RWMA`, `VHD`)** | 3 | **-0.0200** | **-0.0528** | -0.0185 | -0.0094 |
| **Laboratory Panel (14 features)** | 14 | -0.0142 | -0.0189 | **-0.0524** | -0.0121 |
| **Demographics (`Age`, `Sex`, `Weight`, `Length`)** | 4 | -0.0165 | -0.0210 | **-0.0512** | -0.0145 |
| **History & Risk Habits (7 features)** | 7 | -0.0089 | -0.0112 | -0.0105 | **-0.0188** |
| **Resting ECG Findings (7 features)** | 7 | -0.0062 | -0.0085 | -0.0074 | -0.0051 |
| **Single: Typical Chest Pain** | 1 | **-0.0285** | **-0.0238** | -0.0065 | -0.0042 |
| **Single: Age** | 1 | -0.0152 | -0.0194 | **-0.0522** | **-0.0175** |
| **Single: EF-TTE** | 1 | -0.0120 | **-0.0315** | -0.0081 | -0.0062 |
| **Single: Region RWMA** | 1 | -0.0115 | **-0.0298** | -0.0054 | -0.0031 |

---

### Table 12: Exploratory Subgroup Analysis Across Demographic & Clinical Strata
*Authoritative Source: `data/reports/phase4/subgroup_analysis/{target}/{target}_subgroup_analysis.json` and `phase4_master_metrics.json` (Exp E).*  
*Protocol: Feasibility filtering ($N \ge 30, \min(N_+, N_-) \ge 5$). Evaluated on consensus multi-repeat out-of-fold predicted probabilities ($N=303$).*

> **Mandatory Scientific Qualification:**  
> The subgroup performance estimates below represent descriptive, exploratory stratifications within a single-center retrospective cohort ($N=303$). They do not constitute formal algorithmic fairness certification, population equity guarantees, or evidence of causal bias.

| Subgroup Category | Stratum | Stratum Sample Size ($N$) | Positives ($N_+$) | Negatives ($N_-$) | Cath ROC-AUC | LAD ROC-AUC | LCX ROC-AUC | RCA ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Entire Cohort** | All Patients | 303 | 216 | 87 | 0.9097 | 0.8396 | 0.7537 | 0.7200 |
| **Sex** | **Male** | 176 | 130 | 46 | 0.8779 | 0.8579 | 0.7557 | 0.6840 |
| | **Female** | 127 | 86 | 41 | 0.9495 | 0.8102 | 0.7482 | 0.7611 |
| **Age Group** | **Age < 55** | 108 | 68 | 40 | 0.8954 | 0.8569 | 0.7380 | 0.7861 |
| | **Age 55 - 65** | 100 | 78 | 22 | 0.9534 | 0.8451 | 0.7636 | 0.6962 |
| | **Age $\ge$ 65** | 95 | 70 | 25 | 0.7480 | 0.7171 | 0.6055 | 0.6422 |
| **Diabetes (DM)** | **Diabetic** | 90 | 78 | 12 | 0.9838 | 0.6874 | 0.7011 | 0.6174 |
| | **Non-Diabetic** | 213 | 138 | 75 | 0.8843 | 0.8763 | 0.7585 | 0.7099 |
| **Hypertension (HTN)** | **Hypertensive** | 179 | 136 | 43 | 0.8886 | 0.7855 | 0.7203 | 0.6898 |
| | **Normotensive** | 124 | 80 | 44 | 0.8980 | 0.8850 | 0.7585 | 0.7443 |
| **Obesity** | **Obese ($\text{BMI} \ge 25$)** | 211 | 150 | 61 | 0.9128 | 0.8344 | 0.7758 | 0.7255 |
| | **Non-Obese** | 92 | 66 | 26 | 0.9033 | 0.8463 | 0.7030 | 0.7143 |
| **Dyslipidemia (DLP)** | **Dyslipidemic** | 112 | 86 | 26 | 0.9275 | 0.7939 | 0.7422 | 0.7257 |
| | **Non-Dyslipidemic** | 191 | 130 | 61 | 0.9009 | 0.8680 | 0.7598 | 0.7163 |

---

## 7. Literature Review Status & Scientific References

### 7.1 Formal Literature Audit Statement
An exhaustive git history and filesystem audit of the repository was conducted. The audit established that:
1. No dedicated bibliography (`.bib`), citation inventory, or literature review document currently exists within the repository tree.
2. The phrase "16 previously reviewed papers" mentioned in project notes represents an external exploratory reading list from prior project discussions; no bibliographic records, PDFs, or review notes for these 16 papers exist in the repository files.
3. Therefore, no claim is made that these 16 papers have been formally reviewed within this repository. To establish complete scientific traceability for Phase 5.2, an initial categorized inventory of verified and pending literature is established below.

### 7.2 Verified References (Directly Documented and Implemented in Repository)
1. **Lundberg, S. M., & Lee, S.-I.** (2017). A Unified Approach to Interpreting Model Predictions. *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30, 4765–4774. [Establishes unified additive feature attribution and SHAP framework].
2. **Lundberg, S. M., Erion, G., Chen, H., et al.** (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2(1), 56–67. DOI: 10.1038/s42256-019-0138-9. [Establishes exact polynomial-time TreeSHAP algorithm].
3. **Chen, T., & Guestrin, C.** (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16)*, 785–794. DOI: 10.1145/2939672.2939785.
4. **Pedregosa, F., Varoquaux, G., Gramfort, A., et al.** (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
5. **Platt, J. C.** (1999). Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods. *Advances in Large Margin Classifiers*, 10(3), 61–74. [Establishes Platt scaling / sigmoid calibration].
6. **Brier, G. W.** (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3. [Defines Brier score quadratic calibration loss].
7. **BodyParts3D / The Database Center for Life Science (DBCLS)**. Anatomical 3D models licensed under CC BY-SA 2.1 Japan; mapped to Foundational Model of Anatomy (FMA) ontology.

### 7.3 Pending Verification List (Literature Requiring DOI & Retrieval in Phase 5.2)
*The following candidate references will be formally verified against primary publications prior to inclusion in the manuscript bibliography:*
1. **Z-Alizadeh Sani Cohort Studies:**
   - **Alizadeh Sani, Z., et al.** (2013). Computer aided diagnosis of coronary artery disease using genetic algorithm based feature selection. *Computer Methods and Programs in Biomedicine*, 110(3), 432–439. DOI: 10.1016/j.cmpb.2013.01.003.
   - **Alizadeh Sani, Z., et al.** (2017). A data mining approach for diagnosis of coronary artery disease. *Computational Biology and Chemistry*, 73, 134–146. DOI: 10.1016/j.compbiolchem.2017.12.004.
   - **Arabasadi, Z., et al.** (2017). Computer aided decision making for heart disease detection using hybrid neural network-Genetic algorithm. *Computer Methods and Programs in Biomedicine*, 141, 19–26. DOI: 10.1016/j.cmpb.2017.01.004.
   - **Abdar, M., et al.** (2019). A new machine learning technique for predicting coronary artery disease. *Computer Methods and Programs in Biomedicine*, 179, 104992.
2. **Calibration Foundations:**
   - **Niculescu-Mizil, A., & Caruana, R.** (2005). Predicting good probabilities with supervised learning. *Proceedings of the 22nd International Conference on Machine Learning (ICML '05)*, 625–632. DOI: 10.1145/1102351.1102430.
   - **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q.** (2017). On Calibration of Modern Neural Networks. *Proceedings of the 34th International Conference on Machine Learning (ICML 2017)*, PMLR 70, 1321–1330.
   - **Van Calster, B., et al.** (2019). A calibration hierarchy for risk models was defined: from utopia to empirical calibration. *Journal of Clinical Epidemiology*, 110, 29–38. DOI: 10.1016/j.jclinepi.2019.02.017.
3. **Clinical AI Reporting Standards:**
   - **Collins, G. S., Moons, K. G. M., Dhiman, P., et al.** (2024). *TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use machine learning or artificial intelligence*. BMJ 2024;385:e078378. DOI: 10.1136/bmj-2023-078378.
4. **Explainability & Stability Foundations:**
   - **Alvarez-Melis, D., & Jaakkola, T. S.** (2018). Towards Robust Interpretability with Self-Explaining Neural Networks. *NeurIPS 2018*, 31.
   - **Visani, G., Bagli, E., Chesani, F., et al.** (2022). Statistical stability of feature importance in machine learning models. *Data Mining and Knowledge Discovery*, 36, 1269–1314. DOI: 10.1007/s10618-022-00858-5.
5. **Predictive Uncertainty in Clinical Decision Support:**
   - **Kompa, B., Snoek, J., & Beam, A. L.** (2021). Second opinion needed: communicating uncertainty in machine learning for healthcare. *npj Digital Medicine*, 4(1), 4. DOI: 10.1038/s41746-020-00367-3.

---

## 8. Explicit Limitations & Scientific Boundaries

To preserve strict scientific integrity, the manuscript must declare the following boundaries:

1. **Single-Center Retrospective Origin:** The entire cohort consists of $N = 303$ consecutive patients referred for diagnostic catheterization at a single tertiary center (Tehran Heart Center, Iran). Disease prevalence (Cath CAD = 71.29%) reflects tertiary referral patterns and is substantially higher than primary outpatient screening populations.
2. **No External Geographic Validation:** All reported metrics reflect internal repeated cross-validation. No independent cohorts from different geographic regions, hospital systems, or racial demographics were available for external validation.
3. **No Prospective Temporal Validation:** The evaluation does not evaluate temporal generalization across different clinical operating eras or changing clinical protocols.
4. **Correlated Repeated-CV Folds:** The 25 outer cross-validation folds share patient samples across repeats. Metric standard deviations report fold-level resampling dispersion (`ddof=1`) across evaluation splits; they do **not** represent independent-sample population confidence intervals.
5. **Exploratory Nature of Subgroup Findings:** Stratified subgroup sample sizes range from $N = 90$ to $213$ (minority classes within strata $N < 50$). Findings are purely descriptive and hypothesis-generating; no formal demographic parity, equalized odds, or algorithmic fairness guarantees are claimed.
6. **Observational SHAP Attributions:** SHAP feature attributions describe statistical input-output relationships in trained predictive estimators. They do **not** establish biological etiology, clinical causality, or interventional treatment effects.
7. **Non-Linear Calibration vs Linear Attribution Space:** SHAP operates strictly in pre-calibration model-score space ($f(x)$). For Platt-calibrated models, final predicted probabilities are generated via non-linear sigmoid transformation $\sigma(A f(x) + B)$. SHAP attributions cannot be linearly summed to reconstruct final calibrated probabilities.
8. **Exploratory Uncertainty Thresholds:** Evaluated uncertainty boundaries ($H(p) > 0.80$, $|p - \tau| < 0.05$) are computational exploratory simulations. They have **not** been prospectively evaluated in clinical workflows and must **not** be interpreted as clinical referral guidelines, triage rules, or substitutes for physician decision-making.
9. **No Clinical Device Claim:** CoroVista is an academic research software prototype. It has **not** received FDA clearance, CE mark, or regulatory certification, and is not approved for autonomous clinical decision-making.
