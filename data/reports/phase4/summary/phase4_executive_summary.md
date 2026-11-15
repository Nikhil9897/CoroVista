# CoroVista — Phase 4 Research Experiments Executive Summary
## Stability, Uncertainty, Robustness and Subgroup Analysis

**Date:** 2026-11-15 07:45 UTC
**Cohort:** Z-Alizadeh Sani Extension Cohort (303 patients, Tehran Heart Center)
**Evaluation Protocol:** Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats = 25 outer folds)
**Software Stack:** Python 3.11.18, Scikit-Learn 1.7.2, XGBoost 3.2.0, SHAP 0.46.0

---

## 1. Feature-Schema Audit & Discrepancy Resolution

- **Raw workbook total columns:** 59
- **Ground-truth targets excluded from X:** 4 (Cath, LAD, LCX, RCA)
- **Raw feature matrix columns:** 55
- **Zero-variance feature dropped by preprocessing:** 1 (`Exertional CP`, 100% `'N'`)
- **Eligible predictive features entering estimators:** 54
- **Transformed numerical features after One-Hot encoding:** 57 (one-hot `VHD` [4 levels], `BBB` [3 levels])
- **Patient Row Index 93 Preserved:** Yes (Cath=`Normal`, LAD=`Stenotic`, LCX=`Normal`, RCA=`Normal`)

> **Schema Clarification:** Phase 3 documentation references 55 raw non-target features in the patient inference input schema. One feature (`Exertional CP`) has zero variance in the audited 303-patient cohort and is deterministically dropped inside `ClinicalFeatureCleaner`, resulting in exactly 54 active clinical features entering the model pipeline.

---

## 2. Multi-Target Quantitative Summary & Metric Reconciliation

The table below reconciles Phase 3 benchmark standards with Phase 4 stability and ablation evaluations:

| Target | Model Architecture | Calibration Method | Operating Threshold | Phase 3 Benchmark ROC-AUC (25-Fold Mean $\pm$ SD) | Phase 4 Repeated-CV ROC-AUC (25-Fold Mean $\pm$ SD) | Phase 4 Consensus OOF ROC-AUC ($N=303$) | Phase 4 Repeat-1 Ablation Baseline ROC-AUC | SHAP Rank Corr (Mean $\pm$ SD) | 100% Invariant Labels (%) | Mean Prob SD ($\sigma_p$) | Entropy Error AUC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | XGBoost | Sigmoid | 0.50 | $0.9123 \pm 0.0396$ | $0.9128 \pm 0.0406$ | 0.9097 | 0.9018 | $0.932 \pm 0.019$ | 91.1% | 0.038 | 0.759 |
| **LAD** | XGBoost | Sigmoid | 0.50 | $0.8443 \pm 0.0518$ | $0.8427 \pm 0.0553$ | 0.8396 | 0.8477 | $0.922 \pm 0.020$ | 81.8% | 0.049 | 0.659 |
| **LCX** | XGBoost | None | 0.50 | $0.7358 \pm 0.0616$ | $0.7393 \pm 0.0570$ | 0.7537 | 0.7426 | $0.908 \pm 0.026$ | 67.0% | 0.070 | 0.639 |
| **RCA** | Logistic Regression | Sigmoid | 0.35 | $0.7163 \pm 0.0593$ | $0.7163 \pm 0.0592$ | 0.7200 | 0.7040 | $0.774 \pm 0.058$ | 75.6% | 0.040 | 0.680 |

### Metric Definition & Reconciliation Summary
1. **Primary Recommended Manuscript Metric:** **25-Fold Repeated-CV Fold Mean $\pm$ Standard Deviation**. When evaluated on identical 25 outer folds, Phase 3 and Phase 4 results match with statistical equivalence ($p > 0.95$, differences $< 0.0035$ attributable to minor calibration split sub-sampling).
2. **Phase 4 Repeat-1 Ablation Baseline:** In Experiment D, feature ablation was benchmarked against a single 5-fold cross-validation run (Repeat 1, random seed 42) with pooled out-of-fold predictions ($N=303$). These values (0.9018, 0.8477, 0.7426, 0.7040) serve strictly as the internal baseline for ablation delta calculations and must not be conflated with the 25-fold Repeated-CV summary.
3. **Consensus OOF Metric:** In Experiment E, out-of-fold predicted probabilities were averaged across the 5 repeats for each patient ($N=303$), evaluating ensembled multi-repeat stability.

---

## 3. Key Findings Across Research Dimensions

### A. SHAP Explanation Stability
- **Cath & LAD:** High global ranking stability (Spearman rank correlation $\rho > 0.92$ across outer folds). Physiological anchors (`Typical Chest Pain`, `Region RWMA`, `EF-TTE`, `Age`) consistently populate the top 5 across folds.
- **LCX:** Moderate stability ($\rho = 0.9081$, Top-5 Jaccard = 0.5195), reflecting lower minority class prevalence and absence of pathognomonic localizing signs, leading to fold-to-fold alternation among secondary laboratory markers (`CR`, `TG`, `PLT`).
- **RCA:** Moderate stability ($\rho = 0.7737$, Top-5 Jaccard = 0.4890), where regularized Logistic Regression redistributes weights across correlated covariates (`Age`, `DM`, `Function Class`, `Dyspnea`, `ESR`).
- **Exact Reconstruction Verification:** 100% of outer folds across all four targets verified exact additivity in raw model-score/log-odds space within numerical tolerance ($\le 1.19 \times 10^{-6}$ for XGBoost; $\le 1.78 \times 10^{-15}$ for Logistic Regression).
- **Explanation Space Disclosure:** Raw SHAP values explain pre-calibration model scores ($f(x)$) and do not linearly sum to calibrated probabilities.

### B. Prediction Stability & Classification Invariance
- Continuous probability dispersion across repeated outer folds is low (mean per-patient $\sigma_p \in [0.038, 0.070]$ across targets).
- Classification label flips are strictly localized to patients situated in the immediate vicinity of the decision threshold ($|p - \tau| < 0.05$). For patients with confident predictions ($|p - \tau| \ge 0.20$), label invariance exceeds 99%.
- Out-of-fold patient risk rankings are preserved across independent resamplings (Spearman $\rho \ge 0.86$ across all targets).

### C. Uncertainty Estimation & Discrimination
- Binary predictive entropy $H(p)$ correlates with classification errors (error-detection ROC-AUC = 0.759 for Cath, 0.659 for LAD, 0.639 for LCX, 0.680 for RCA).
- Distance from threshold $|p - \tau|$ correlates inversely with empirical error rate in this cohort.
- **Scientific Clarification:** Entropy is a mathematical property of the predicted probability, not a calibrated probability of error. The evaluated thresholds ($H(p) > 0.80$, $|p - \tau| < 0.05$) are exploratory research thresholds and do not represent clinically validated decision or triage rules.

### D. Robustness & Stress Testing
- Under controlled additive Gaussian noise ($\pm 0.5\sigma$), classification flip rates remain below 4.3% for tree models and 6.8% for logistic regression.
- Internal median imputation maintains discrimination under synthetic MCAR missingness up to 20%.
- Inside-CV feature ablation reveals that Echocardiography (`EF-TTE`, `Region RWMA`) and Clinical Symptoms (`Typical Chest Pain`) provide the highest marginal performance contributions for Cath and LAD, whereas LCX depends predominantly on Laboratory Panels and Demographics.

### E. Exploratory Subgroup Analysis
- Feasible strata ($N \ge 30, \min(N_+, N_-) \ge 5$): Male ($N=176$), Female ($N=127$), Age $<55$ ($N=108$), Age 55–65 ($N=100$), Age $\ge 65$ ($N=95$), Diabetic ($N=90$), Non-Diabetic ($N=213$), Hypertensive ($N=179$), Normotensive ($N=124$), Obese ($N=211$), Non-Obese ($N=92$), Dyslipidemic ($N=112$), Non-Dyslipidemic ($N=191$).
- **Descriptive Differences:** Lower descriptive ROC-AUC estimates were observed in the older age stratum ($\ge 65$ years, $N = 95$) in this cohort. The current analysis does not establish the clinical or statistical mechanisms underlying these differences. These observations are hypothesis-generating and require independent validation.
- **Scientific Disclaimers:** Subgroup findings represent descriptive internal stratifications within a single-center cohort ($N=303$). They do not establish algorithmic bias, demographic fairness, or population-level disparities.

---

## 4. Mandatory Clinical & Methodological Disclaimers

> [!WARNING]
> **Clinical Disclaimer:** All uncertainty, deferral, and stability analyses are exploratory computational investigations. The proposed thresholds have not been clinically validated and must not be interpreted as diagnostic, referral, or triage recommendations. Independent external validation and prospective clinical evaluation are necessary before any clinical application.

> [!NOTE]
> **Methodological Limitations:** All evaluations were conducted on a single-center retrospective cohort ($N=303$, Tehran Heart Center). Repeated cross-validation reuses the same patient cohort; observations across folds are correlated and do not constitute independent external validation. SHAP attributions reflect associative model weights, not biological causal effects.

---

## 5. Verification & Production Artifact Integrity

- Production model artifacts in `models/{cad,lad,lcx,rca}`: **UNTOUCHED**
- All 37 unit, integration, explainability, and research regression tests: **PASSED**
- Ruff code formatting and linting: **PASSED (0 violations)**
- **Status of Unresolved Research Issues:** Reporting inconsistencies identified during this validation pass have been addressed. Important research limitations remain, including the absence of external validation, prospective clinical evaluation, and independent subgroup validation. These limitations must be considered during manuscript preparation.
