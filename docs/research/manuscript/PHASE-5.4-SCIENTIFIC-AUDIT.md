# Phase 5.4: Final Scientific Audit & Manuscript Verification Report

**Project:** CoroVista — Coronary Artery Disease Prediction & Explainability  
**Document Type:** Independent Scientific Audit, Biomedical ML Review & Quality Control Verification  
**Auditor Role:** Independent Scientific Auditor & Biomedical Machine Learning Reviewer  
**Date:** November 15, 2026  
**Repository Branch:** `development`  
**Primary Target Document:** `docs/research/manuscript/CoroVista-Research-Manuscript.md`  
**Supporting Documents:**
- `docs/research/manuscript/01-abstract-introduction-related-work.md`
- `docs/research/manuscript/02-methods-and-results.md`
- `docs/research/manuscript/03-discussion-limitations-conclusion.md`
- `docs/research/manuscript/references.md`
- `docs/research/manuscript/MANUSCRIPT-EDITORIAL-REVIEW.md`
- `docs/research/PHASE-5.1-MANUSCRIPT-EVIDENCE-MATRIX.md`
- `docs/research/PHASE-5.1-OPEN-ISSUES.md`

---

## 1. Executive Summary & Audit Verdict

### Overall Audit Verdict: **PASS WITH CORRECTIONS**

The CoroVista research manuscript entitled *"Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness"* has undergone a comprehensive, multi-dimensional scientific audit. 

The mathematical framework, machine learning methodology, cross-validation isolation, and numerical results exhibit an exceptionally high standard of scientific integrity:
1. **Zero Data Leakage:** Preprocessing, imputation, encoding, and Platt (Sigmoid) calibration are strictly isolated within cross-validation folds.
2. **100% Numerical Fidelity:** All reported discrimination metrics, calibration errors (Brier, ECE), SHAP stability coefficients, prediction flip rates, uncertainty metrics, and ablation deltas exactly match the locked Phase 5.1 evidence matrix and underlying JSON experiment outputs.
3. **Rigorous Sample Variance Reporting:** All 25-fold outer test metrics properly report sample standard deviation ($ddof=1$) alongside population standard deviation ($ddof=0$), completely resolving historical ambiguities.
4. **Prudent Clinical Claim Boundaries:** The manuscript strictly avoids unjustified claims of clinical readiness, diagnostic autonomy, biological causality, or algorithmic fairness.

However, the audit identified **one Critical institutional attribution discrepancy** and **two Major bibliographic mapping omissions** that must be rectified before journal submission:
- **[CRITICAL] Cohort Institutional Misattribution:** The cohort has been erroneously attributed to *"Tehran Heart Center"* in the drafts. Authoritative bibliographic and repository provenance confirms the true patient origin is **Shaheed Rajaei Cardiovascular, Medical and Research Center** (Tehran, Iran).
- **[MAJOR] Unlinked In-Text Citations:** References for Scikit-learn (`Pedregosa et al., 2011`) and BodyParts3D (`Mitsuhashi et al., 2009`) are present in the bibliography but lacked parenthetical in-text citations in the manuscript body.
- **[MINOR] TRIPOD+AI Wording Calibration:** Claims regarding TRIPOD+AI compliance require slight qualification to reflect academic reporting alignment.

With these corrections applied and logged, the manuscript satisfies all publication-readiness criteria for submission to peer-reviewed biomedical machine learning and clinical informatics journals.

---

## 2. Comprehensive Numerical Verification Matrix

Every quantitative claim, table entry, and inline statistic in `docs/research/manuscript/CoroVista-Research-Manuscript.md` was audited against primary raw data sources:
- `data/reports/dataset_audit.json`
- `data/reports/reproduction_audit/model_benchmark.json`
- `data/reports/reproduction_audit/calibration_results.json`
- `data/reports/phase4/summary/phase4_master_metrics.json`
- `docs/research/PHASE-5.1-MANUSCRIPT-EVIDENCE-MATRIX.md`

| # | Scientific Claim / Metric | Manuscript Value | Authoritative Source Value | Source Artifact & Key | Verification Status | Notes / Correction Required |
| :-: | :--- | :--- | :--- | :--- | :-: | :--- |
| 1 | Cohort Size ($N$) | 303 patients | 303 patients | `dataset_audit.json`: `n_rows` | **VERIFIED** | Matches perfectly. |
| 2 | Active Clinical Features | 54 features | 54 features (59 raw columns minus 4 targets and 1 ID) | `dataset_audit.json`: `n_columns` | **VERIFIED** | Post-OHE dimension is 57. |
| 3 | Target: Cath Prevalence | 71.29% (216/303) | 71.29% (216 CAD, 87 Normal) | `dataset_audit.json`: `targets_audit.Cath` | **VERIFIED** | Matches perfectly. |
| 4 | Target: LAD Prevalence | 58.42% (177/303) | 58.42% (177 Stenotic, 126 Normal) | `dataset_audit.json`: `targets_audit.LAD` | **VERIFIED** | Matches perfectly. |
| 5 | Target: LCX Prevalence | 39.27% (119/303) | 39.27% (119 Stenotic, 184 Normal) | `dataset_audit.json`: `targets_audit.LCX` | **VERIFIED** | Matches perfectly. |
| 6 | Target: RCA Prevalence | 37.62% (114/303) | 37.62% (114 Stenotic, 189 Normal) | `dataset_audit.json`: `targets_audit.RCA` | **VERIFIED** | Matches perfectly. |
| 7 | Cath - LAD/LCX/RCA Concordance | 99.67% (302/303) | 99.67% (1 discordance) | `dataset_audit.json`: `cath_vessel_mismatches` | **VERIFIED** | Patient Index 93 preserved. |
| 8 | Patient Age (Mean $\pm$ SD) | $58.898 \pm 10.392$ | Mean 58.898, SD 10.392 | `dataset_audit.json`: `numerical_statistics.Age` | **VERIFIED** | Range: 30 to 86 years. |
| 9 | Patient Sex (Male / Female) | 176 (58.09%) / 127 (41.91%) | Male: 176, Female: 127 | `dataset_audit.json`: `categorical_statistics.Sex` | **VERIFIED** | Matches raw records. |
| 10 | Cath XGBoost Sigmoid ROC-AUC | $0.9123 \pm 0.0404$ [`ddof=1`]<br>[$0.0396$ `ddof=0`] | Mean: 0.9123, SD (ddof=1): 0.0404, SD (ddof=0): 0.0396 | `model_benchmark.json`: `Cath.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Dual SD reporting clarifies variance. |
| 11 | Cath XGBoost Sigmoid PR-AUC | $0.9597 \pm 0.0200$ [`ddof=1`]<br>[$0.0196$ `ddof=0`] | Mean: 0.9597, SD (ddof=1): 0.0200, SD (ddof=0): 0.0196 | `model_benchmark.json`: `Cath.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. |
| 12 | Cath XGBoost Sigmoid Brier Score | $0.1034 \pm 0.0251$ [`ddof=1`]<br>[$0.0246$ `ddof=0`] | Mean: 0.1034, SD (ddof=1): 0.0251, SD (ddof=0): 0.0246 | `model_benchmark.json`: `Cath.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. Raw uncalibrated: 0.1074. |
| 13 | Cath XGBoost Sigmoid ECE | $0.1004 \pm 0.0227$ [`ddof=1`]<br>[$0.0222$ `ddof=0`] | Mean: 0.1004, SD (ddof=1): 0.0227, SD (ddof=0): 0.0222 | `model_benchmark.json`: `Cath.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. Raw uncalibrated: 0.1265. |
| 14 | LAD XGBoost Sigmoid ROC-AUC | $0.8443 \pm 0.0528$ [`ddof=1`]<br>[$0.0518$ `ddof=0`] | Mean: 0.8443, SD (ddof=1): 0.0528, SD (ddof=0): 0.0518 | `model_benchmark.json`: `LAD.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. |
| 15 | LAD XGBoost Sigmoid PR-AUC | $0.8818 \pm 0.0471$ [`ddof=1`]<br>[$0.0462$ `ddof=0`] | Mean: 0.8818, SD (ddof=1): 0.0471, SD (ddof=0): 0.0462 | `model_benchmark.json`: `LAD.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. |
| 16 | LAD XGBoost Sigmoid Brier Score | $0.1609 \pm 0.0226$ [`ddof=1`]<br>[$0.0221$ `ddof=0`] | Mean: 0.1609, SD (ddof=1): 0.0226, SD (ddof=0): 0.0221 | `model_benchmark.json`: `LAD.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. Raw uncalibrated: 0.1651. |
| 17 | LAD XGBoost Sigmoid ECE | $0.1326 \pm 0.0394$ [`ddof=1`]<br>[$0.0386$ `ddof=0`] | Mean: 0.1326, SD (ddof=1): 0.0394, SD (ddof=0): 0.0386 | `model_benchmark.json`: `LAD.calibration_comparison.XGBoost_sigmoid` | **VERIFIED** | Matches. Raw uncalibrated: 0.1434. |
| 18 | LCX XGBoost Uncalibrated ROC-AUC | $0.7358 \pm 0.0629$ [`ddof=1`]<br>[$0.0616$ `ddof=0`] | Mean: 0.7358, SD (ddof=1): 0.0629, SD (ddof=0): 0.0616 | `model_benchmark.json`: `LCX.calibration_comparison.XGBoost_uncalibrated` | **VERIFIED** | Uncalibrated selected to preserve resolution. |
| 19 | LCX XGBoost Uncalibrated PR-AUC | $0.6173 \pm 0.0838$ [`ddof=1`]<br>[$0.0821$ `ddof=0`] | Mean: 0.6173, SD (ddof=1): 0.0838, SD (ddof=0): 0.0821 | `model_benchmark.json`: `LCX.calibration_comparison.XGBoost_uncalibrated` | **VERIFIED** | Matches. |
| 20 | LCX XGBoost Uncalibrated Brier Score | $0.2054 \pm 0.0240$ [`ddof=1`]<br>[$0.0235$ `ddof=0`] | Mean: 0.2054, SD (ddof=1): 0.0240, SD (ddof=0): 0.0235 | `model_benchmark.json`: `LCX.calibration_comparison.XGBoost_uncalibrated` | **VERIFIED** | Matches. |
| 21 | LCX XGBoost Uncalibrated ECE | $0.1366 \pm 0.0315$ [`ddof=1`]<br>[$0.0309$ `ddof=0`] | Mean: 0.1366, SD (ddof=1): 0.0315, SD (ddof=0): 0.0309 | `model_benchmark.json`: `LCX.calibration_comparison.XGBoost_uncalibrated` | **VERIFIED** | Matches. |
| 22 | RCA LogReg Sigmoid ROC-AUC | $0.7163 \pm 0.0605$ [`ddof=1`]<br>[$0.0593$ `ddof=0`] | Mean: 0.7163, SD (ddof=1): 0.0605, SD (ddof=0): 0.0593 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid` | **VERIFIED** | Linear model selected for diffuse target. |
| 23 | RCA LogReg Sigmoid PR-AUC | $0.6098 \pm 0.0775$ [`ddof=1`]<br>[$0.0759$ `ddof=0`] | Mean: 0.6098, SD (ddof=1): 0.0775, SD (ddof=0): 0.0759 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid` | **VERIFIED** | Matches. |
| 24 | RCA LogReg Sigmoid Brier Score | $0.2060 \pm 0.0150$ [`ddof=1`]<br>[$0.0147$ `ddof=0`] | Mean: 0.2060, SD (ddof=1): 0.0150, SD (ddof=0): 0.0147 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid` | **VERIFIED** | Lowest Brier score on RCA. |
| 25 | RCA LogReg Sigmoid ECE | $0.1000 \pm 0.0321$ [`ddof=1`]<br>[$0.0315$ `ddof=0`] | Mean: 0.1000, SD (ddof=1): 0.0321, SD (ddof=0): 0.0315 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid` | **VERIFIED** | Matches. |
| 26 | RCA Standard Cutoff ($\tau=0.50$) Recall | $31.24\% \pm 8.56\%$ [`ddof=1`] | Mean: 0.3124, SD (ddof=1): 0.0856 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid.standard_threshold_metrics.recall` | **VERIFIED** | Demonstrates clinical sensitivity collapse. |
| 27 | RCA Nested Tuned Cutoff | $0.3188 \pm 0.0380$ [`ddof=1`]<br>[$0.0372$ `ddof=0`] | Mean: 0.3188, SD (ddof=1): 0.0380, SD (ddof=0): 0.0372 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid.selected_thresholds` | **VERIFIED** | Audited from 25 raw outer fold values. |
| 28 | RCA Nested Tuned Recall | $79.46\% \pm 10.92\%$ [`ddof=1`]<br>[$10.70\%$ `ddof=0`] | Mean: 0.7946, SD (ddof=1): 0.1092, SD (ddof=0): 0.1070 | `model_benchmark.json`: `RCA.calibration_comparison.LogisticRegression_sigmoid.tuned_threshold_metrics.recall` | **VERIFIED** | Restores sensitivity on minority target. |
| 29 | RCA Nested Tuned Specificity | $49.41\% \pm 14.29\%$ [`ddof=1`]<br>[$10.93\%$ 5-repeat SD] | 25-fold Mean: 0.4941, Fold SD: 0.1429, 5-Repeat Mean: 0.4941, Repeat SD: 0.1093 | `model_benchmark.json` and `phase4_master_metrics.json` | **VERIFIED** | Both protocol SDs explicitly disclosed. |
| 30 | RCA Fixed Production Cutoff ($\tau=0.35$) | Recall $74.21\% \pm 10.64\%$ Specificity $57.48\% \pm 7.10\%$ | Recall: 0.7421 ± 0.1064, Specificity: 0.5748 ± 0.0710 | `model_benchmark.json`: 5-repeat summary | **VERIFIED** | Correctly segregated from 25-fold nested. |
| 31 | SHAP Additivity Check | 100% (25/25 outer folds) | All 25 folds passed, max error $< 1.19 \times 10^{-6}$ | `phase4_master_metrics.json`: `target_results.*.reconstruction_check` | **VERIFIED** | TreeSHAP & LinearSHAP exact additivity. |
| 32 | Cath TreeSHAP Global Spearman $\rho$ | $0.9319 \pm 0.0192$ | Mean: 0.9319, SD: 0.0192 (300 pairs) | `phase4_master_metrics.json`: `target_results.Cath.exp_a.global_stability.spearman_rank_correlation` | **VERIFIED** | High global explanation stability. |
| 33 | Cath Prediction Flips ($|p-\tau| < 0.05$) | 100% flips (6/6 patients, 0% invariant) | 6 patients, 0% perfect agreement, flip rate 100% | `phase4_master_metrics.json`: `target_results.Cath.exp_b.classification_stability.threshold_proximity_stratification` | **VERIFIED** | Overconfident legacy wording corrected. |
| 34 | Cath Confident Invariance ($|p-\tau| \ge 0.20$) | 99.2% invariant (244/246 patients) | 246 patients, 244 invariant (99.19%), 2 flipped | `phase4_master_metrics.json`: `target_results.Cath.exp_b.classification_stability.threshold_proximity_stratification` | **VERIFIED** | Confirmed 2 patients flipped outside band. |
| 35 | Binary Predictive Entropy AUC | 0.7593 for Cath error detection | AUC: 0.759285 | `phase4_master_metrics.json`: `target_results.Cath.exp_c.entropy_uncertainty.entropy_error_auc` | **VERIFIED** | Unsupervised error triage validated. |
| 36 | Inside-CV Ablation: LAD vs LCX | LAD: RWMA drop $-0.0435$<br>LCX: Lab drop $-0.0454$ | LAD RWMA: $-0.0435$<br>LCX Labs: $-0.0454$ | `phase4_master_metrics.json`: `target_results.*.exp_d.feature_ablation` | **VERIFIED** | Confirms contrasting territorial drivers. |

---

## 3. Dataset Provenance & Institutional Identity Audit

### The Discrepancy: "Tehran Heart Center" vs. "Shaheed Rajaei Cardiovascular, Medical and Research Center"

#### Provenance Investigation Findings
During the Phase 5.4 provenance audit, all primary literature associated with the Z-Alizadeh Sani cohort was examined:
1. **Alizadehsani et al. (2013)** (*Computer Methods and Programs in Biomedicine*, 111(1), 52–61, DOI: 10.1016/j.cmpb.2013.03.004):
   - Co-author **Dr. Zahra Alizadeh Sani** is an interventional cardiologist and Associate Professor of Cardiology at **Shaheed Rajaei Cardiovascular, Medical and Research Center**, School of Medicine, Iran University of Medical Sciences, Tehran, Iran.
   - The paper states: *"The dataset was collected from Shaheed Rajaei Cardiovascular, Medical and Research Center."*
2. **UCI Machine Learning Repository Citation** (Alizadehsani, 2017, DOI: 10.24432/C5Q31T):
   - Dataset metadata lists donor affiliation: *Shaheed Rajaei Cardiovascular, Medical and Research Center, Tehran, Iran*.
3. **Mendeley Data Repository Citation** (Alizadehsani, 2018, DOI: 10.17632/9k56pwtvz9.1):
   - Dataset metadata reaffirms origin at *Shaheed Rajaei Cardiovascular, Medical and Research Center*.
4. **Distinct Institutional Identity:**
   - *Tehran Heart Center* (affiliated with Tehran University of Medical Sciences) is an entirely independent cardiovascular tertiary hospital located on North Kargar Avenue, Tehran.
   - *Shaheed Rajaei Cardiovascular, Medical and Research Center* (also known as Rajaie Cardiovascular Medical and Research Center, affiliated with Iran University of Medical Sciences) is located on Vali-Asr Street, Tehran.
   - Attributing the patient records to Tehran Heart Center represents an institutional misattribution that would misinform peer reviewers and readers.

#### Audit Action & Resolution
- **Status:** **CRITICAL FINDING — RESOLVED VIA CORRECTION**
- All 8 occurrences of "Tehran Heart Center" across the manuscript (`CoroVista-Research-Manuscript.md`), supporting drafts (`01-*`, `02-*`, `03-*`), references document (`references.md`), and editorial review (`MANUSCRIPT-EDITORIAL-REVIEW.md`) have been systematically replaced with **"Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran)"**.
- Section 3.1, Section 6.1 (Limitations), Declarations, and the Abstract now correctly document the true clinical provenance.

---

## 4. Bibliographic & Reference Verification Audit

The manuscript bibliography contains 22 verified citations. Each reference was verified for bibliographic completeness, author roster, title accuracy, journal venue, publication year, and digital object identifier (DOI) / URL resolution.

### Reference Audit & In-Text Citation Mapping

| # | Reference Key | Type | Venue / DOI / URL | In-Text Citation in Draft | Final Mapping Status | Correction Required |
| :-: | :--- | :--- | :--- | :-: | :-: | :--- |
| 1 | Abdar et al. (2019) | Journal Article | *CMPB* / 10.1016/j.cmpb.2019.104992 | Yes (Sec 2.1) | **VERIFIED** | None. |
| 2 | Alizadehsani (2017) | Data Repository | *UCI ML Repository* / 10.24432/C5Q31T | Yes (Sec 3.1, Decl) | **VERIFIED** | None. |
| 3 | Alizadehsani (2018) | Data Repository | *Mendeley Data* / 10.17632/9k56pwtvz9.1 | Yes (Sec 3.1, Decl) | **VERIFIED** | None. |
| 4 | Alizadehsani et al. (2013) | Journal Article | *CMPB* / 10.1016/j.cmpb.2013.03.004 | Yes (Sec 1.1, 2.1, 3.1) | **VERIFIED** | Center updated to Shaheed Rajaei. |
| 5 | Alizadehsani et al. (2018) | Journal Article | *CMPB* / 10.1016/j.cmpb.2018.05.009 | Yes (Sec 2.2, 3.1) | **VERIFIED** | None. |
| 6 | Alvarez-Melis & Jaakkola (2018) | Conference Paper | *NeurIPS 2018* / Proceedings URL | Yes (Sec 1.2, 2.4, 3.4) | **VERIFIED** | None. |
| 7 | Arabasadi et al. (2017) | Journal Article | *CMPB* / 10.1016/j.cmpb.2017.01.004 | Yes (Sec 2.1) | **VERIFIED** | None. |
| 8 | Brier (1950) | Foundational Article | *MWR* / 10.1175/1520-0493(1950)... | Yes (Sec 1.2, 2.3, 3.3, 5.2) | **VERIFIED** | None. |
| 9 | Chen & Guestrin (2016) | Conference Paper | *ACM KDD '16* / 10.1145/2939672.2939785 | Yes (Sec 3.3) | **VERIFIED** | None. |
| 10 | Collins et al. (2024) | Statement / Guideline | *BMJ* / 10.1136/bmj-2023-078378 | Yes (Sec 1.3, 3.2, 6.2) | **VERIFIED** | Qualified wording. |
| 11 | Guo et al. (2017) | Conference Paper | *ICML 2017* / PMLR URL | Yes (Sec 1.2, 2.3, 3.3, 5.2) | **VERIFIED** | None. |
| 12 | Kompa et al. (2021) | Journal Article | *npj Digital Med* / 10.1038/s41746-020-00367-3 | Yes (Sec 1.2, 2.4, 3.6, 5.4) | **VERIFIED** | None. |
| 13 | Lawton et al. (2022) | Clinical Practice Guideline | *Circulation* / 10.1161/CIR.0000000000001038 | Yes (Sec 1.1, 2.2, 3.1, 5.1) | **VERIFIED** | None. |
| 14 | Lundberg & Lee (2017) | Conference Paper | *NeurIPS 2017* / Proceedings URL | Yes (Sec 1.2, 2.4, 3.4) | **VERIFIED** | None. |
| 15 | Lundberg et al. (2020) | Journal Article | *Nature Mach Intell* / 10.1038/s42256-019-0138-9 | Yes (Sec 2.4, 3.4, 5.3) | **VERIFIED** | None. |
| 16 | Martin et al. (2024) | Statistical Update | *Circulation* / 10.1161/CIR.0000000000001209 | Yes (Sec 1.1) | **VERIFIED** | None. |
| 17 | Mitsuhashi et al. (2009) | Database Issue Article | *Nucleic Acids Res* / 10.1093/nar/gkn613 | **MISSING IN BODY (0 matches)** | **CORRECTED** | Added in Sec 1.3, 3.1 & Decl. |
| 18 | Niculescu-Mizil & Caruana (2005) | Conference Paper | *ICML '05* / 10.1145/1102351.1102430 | Yes (Sec 2.3, 3.3, 5.2) | **VERIFIED** | None. |
| 19 | Pedregosa et al. (2011) | Software / JMLR Article | *JMLR* / JMLR URL | **MISSING IN BODY (0 matches)** | **CORRECTED** | Added in Sec 3.3 (scikit-learn). |
| 20 | Platt (1999) | Book Chapter / Paper | *Adv Large Margin Classif* / Paper URL | Yes (Sec 1.2, 2.3, 3.3, 5.2) | **VERIFIED** | None. |
| 21 | Van Calster et al. (2019) | Journal Article | *J Clin Epidemiol* / 10.1016/j.jclinepi.2019.02.017 | Yes (Sec 1.2, 2.3, 3.3, 5.2) | **VERIFIED** | None. |
| 22 | Visani et al. (2022) | Journal Article | *Data Min Knowl Disc* / 10.1007/s10618-022-00858-5 | Yes (Sec 1.2, 2.4, 3.4, 5.3) | **VERIFIED** | None. |

---

## 5. Methodological & Scientific Quality Audit

### 5.1 Data Partition Isolation & Leakage Prevention
- **Leakage Risk Assessment:** Zero data leakage. All feature transformations (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`) and calibration wrappers (`CalibratedClassifierCV`) are strictly encapsulated inside scikit-learn pipeline objects fit solely on the training splits of each outer fold.
- **Categorical Feature Encoding:** One-hot encoding handles unseen categories gracefully (`handle_unknown='ignore'`).
- **Feature Exclusions:** Arbitrary record-dropping was avoided. The single anatomical discordance (patient Index 93: `Cath='Normal'` but `LAD='Stenotic'`) is explicitly documented and retained to preserve ecological validity.

### 5.2 Resampling & Cross-Validation Architecture
- **Protocol:** 25-fold Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats, seed 42).
- **Independence Clarification:** The manuscript explicitly clarifies in Sections 3.3, 4.1, and 6.2 that repeated-CV folds are resampled from the same underlying cohort and do not constitute independent external validation datasets.
- **Dispersion Metrics:** The manuscript provides dual standard deviation reporting: unbiased sample standard deviation ($ddof=1$) for fold-to-fold variability, alongside population standard deviation ($ddof=0$) to reconcile legacy benchmark JSON files.

### 5.3 Calibration & Scoring Rules
- **Proper Scoring Rules:** Evaluated using Brier score (mean squared error of predicted probabilities) and Expected Calibration Error (ECE) across 10 equal-width bins.
- **Model Selection Nuance:** Accurately explains why sigmoid calibration was retained for `Cath`, `LAD`, and `RCA`, whereas `LCX` production uses the uncalibrated XGBoost model to prevent post-hoc probability flattening and retain ranking resolution.

### 5.4 Decision Threshold Determination Protocols
- **Strict Protocol Separation:** Meticulously separates:
  1. *Standard Arbitrary Threshold ($\tau=0.50$):* Evaluated across 25 outer test folds.
  2. *Nested Inner-OOF Tuned Threshold:* Optimized exclusively on inner cross-validation folds using the $F_1$-score objective ($0.3188 \pm 0.0380$ for RCA) and evaluated on held-out outer folds.
  3. *Fixed Production Threshold ($\tau=0.35$):* Evaluated via 5 repeated cross-validation runs to assess patient-level consensus behavior.
- **Resolved Bessel Correction:** Verified that the true sample standard deviation of RCA tuned cutoffs across the 25 outer folds is **$0.0380$** (population SD is $0.0372$); the legacy figure of $0.0388$ was an accidental double-Bessel multiplication ($0.0380 \times \sqrt{25/24}$) and has been retired.

### 5.5 Explainability & SHAP Stability Auditing
- **Additivity Verification:** Exact floating-point additivity ($\sum \phi_i + \phi_0 = f(x)$) verified in 100% of folds (25/25) with maximum absolute error $< 1.19 \times 10^{-6}$.
- **Attribution Space Integrity:** SHAP explanations are evaluated in log-odds margin space ($f(x)$) for tree ensembles and decision function space for logistic regression, preventing non-linear sigmoid distortions.
- **Stability Metrics:** Global feature importance ranking stability across 300 pairwise outer fold comparisons quantified via Spearman $\rho$ and Kendall $\tau$, complemented by top-5/top-10 Jaccard overlap and patient-level sign consistency.

### 5.6 Defensive Uncertainty Quantification
- **Normalized Binary Predictive Entropy:** Evaluates $H(p) = -[p \log_2 p + (1-p) \log_2(1-p)]$ as an unsupervised indicator of predictive ambiguity.
- **Error Detection Efficacy:** Successfully discriminates empirical misclassifications without ground-truth labels (ROC-AUC $0.7593$ for Cath).

### 5.7 Scientific Claim Boundaries & Translational Humility
- **Clinical Scope:** Explicitly declared as an academic prototype not cleared for autonomous clinical use.
- **Causality:** Feature attributions explicitly designated as associative statistical properties of trained models, not causal biological mechanisms.
- **Fairness:** Subgroup audits across 13 strata explicitly stated as exploratory, hypothesis-generating observations, not algorithmic fairness certifications.

---

## 6. TRIPOD+AI Itemized Compliance Checklist Assessment

The manuscript reporting was audited against the updated 2024 TRIPOD+AI guidelines (Collins et al., 2024):

| Item # | TRIPOD+AI Item Description | Manuscript Location | Compliance Assessment & Justification |
| :-: | :--- | :--- | :--- |
| **1** | Title: Identify study as developing/evaluating a prediction model using AI/ML | Title, Abstract | **Compliant:** Title includes *"Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability..."* |
| **2** | Abstract: Structured summary (Background, Methods, Results, Conclusions) | Abstract (lines 13–25) | **Compliant:** Fully structured with exact quantitative performance and stability metrics. |
| **3a** | Background: Medical context and rationale for prediction model | Section 1.1, 1.2 | **Compliant:** Outlines CAD epidemiology, catheterization referral burden, and clinical motivation. |
| **3b** | Objectives: Specific study aims and intended clinical use | Section 1.3 | **Compliant:** Defines multi-target epicardial scope and reliability audit goals. |
| **4a** | Source of data: Study design, cohort source, center, dates | Section 3.1 | **Compliant:** Retrospective consecutive cohort at Shaheed Rajaei Cardiovascular Center detailed. |
| **4b** | Eligibility criteria: Inclusion and exclusion criteria | Section 3.1 | **Compliant:** Adult patients referred for catheterization with suspected CAD / stable angina. |
| **5a** | Outcome: Definition of all clinical outcomes and assessment method | Section 3.1 | **Compliant:** $\ge 50\%$ diameter stenosis on invasive angiography defined for Cath, LAD, LCX, RCA. |
| **5b** | Outcome: Blinded outcome assessment | Section 3.1 | **Compliant:** Angiography interpreted by expert cardiologists independently of algorithmic modeling. |
| **6a** | Predictors: Definitions, handling of candidate predictors | Section 3.1, 3.2, Table 1–2 | **Compliant:** 54 clinical features described across demographic, symptom, ECG, lab, echo domains. |
| **6b** | Predictors: Blinded assessment of predictors | Section 3.1 | **Compliant:** Features collected pre-catheterization during standard admission workup. |
| **7** | Sample size: Rationale and cohort size | Section 3.1, 6.1 | **Compliant:** Complete consecutive cohort ($N=303$); sample size limitations discussed. |
| **8** | Missing data: Handling of missing values | Section 3.2, Table 2 | **Compliant:** 0% missingness in active features verified; median/mode imputer included defensively. |
| **9a** | Model development: Architecture, hyperparameters, feature selection | Section 3.2, 3.3 | **Compliant:** Full hyperparameter specifications for XGBoost, Random Forest, Logistic Regression. |
| **9b** | Model development: Resampling, cross-validation, partition isolation | Section 3.3 | **Compliant:** 25-fold Repeated Stratified CV with strict partition isolation detailed. |
| **10a** | Model evaluation: Discrimination and calibration metrics | Section 3.3, 4.1, Table 3–5 | **Compliant:** ROC-AUC, PR-AUC, Brier score, ECE reported with sample standard deviations. |
| **10b** | Model evaluation: Operating threshold optimization | Section 3.3, 4.2, Table 4 | **Compliant:** Nested inner-OOF $F_1$ optimization and fixed cutoffs rigorously separated. |
| **11** | Model explainability: Feature attribution and stability | Section 3.4, 4.3, Table 6–7 | **Compliant:** TreeSHAP/LinearSHAP additivity and 25-fold rank stability quantified. |
| **12** | Participants: Patient flow and baseline characteristics | Section 4.1, Table 1 | **Compliant:** Complete cohort characteristics broken down by CAD status ($N=303$). |
| **13** | Model performance: Numerical results with confidence/dispersion | Section 4.1–4.6, Tables 3–12 | **Compliant:** All metrics reported with mean $\pm$ sample SD (`ddof=1`). |
| **14** | Discussion: Interpretation, clinical relevance, and comparisons | Section 5.1–5.4 | **Compliant:** Detailed interpretation of territorial signals, calibration, and prediction churn. |
| **15** | Limitations: Center bias, lack of external validation, small cohort | Section 6.1–6.2 | **Compliant:** Transparently acknowledges single-center origin, referral bias, and prototype scope. |
| **16** | Declarations: Funding, competing interests, data/code availability | Section 7, Declarations | **Compliant:** Complete disclosures, open data links (UCI, Mendeley), and reproducibility details. |

---

## 7. Deficiencies & Severity Classification

| Issue ID | Severity | Category | File & Location | Description of Deficiencies | Action / Correction Implemented |
| :-: | :---: | :---: | :--- | :--- | :--- |
| **ISS-01** | **Critical** | Provenance | `CoroVista-Research-Manuscript.md` (Lines 17, 83, 93, 181, 187, 773, 820, 870) | Cohort institution misidentified as "Tehran Heart Center" instead of "Shaheed Rajaei Cardiovascular, Medical and Research Center". | Replaced all 8 occurrences with "Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran)". |
| **ISS-02** | **Major** | Citations | `CoroVista-Research-Manuscript.md` (Lines 236–240) | Scikit-learn reference (`Pedregosa et al., 2011`) present in bibliography (#19) but lacked parenthetical in-text citation in body text. | Added `(Pedregosa et al., 2011)` to Section 3.3 candidate architectures and software pipeline description. |
| **ISS-03** | **Major** | Citations | `CoroVista-Research-Manuscript.md` (Lines 69, 196, 839) | BodyParts3D reference (`Mitsuhashi et al., 2009`) present in bibliography (#17) but lacked parenthetical in-text citation in body text. | Added `(Mitsuhashi et al., 2009)` to Section 1.3, Section 3.1, and Authors' Contributions declarations. |
| **ISS-04** | **Minor** | Reporting | `CoroVista-Research-Manuscript.md` (Line 78) | Phrasing "strict alignment with the updated TRIPOD+AI guidelines" sounded overly affirmative for an academic prototype. | Refined to "reporting informed by and aligned with the updated TRIPOD+AI guidelines (Collins et al., 2024)". |
| **ISS-05** | **Informational** | Data Ethics | `CoroVista-Research-Manuscript.md` (Lines 187, 820, 870) | Original 2013 publication does not publish an IRB/ethics committee protocol identifier for this retrospective open dataset. | Maintained explicit `[CITATION NEEDED]` / `[UNRESOLVED]` disclosure notes in Section 3.1 and Declarations. |
| **ISS-06** | **Informational** | Literature | `CoroVista-Research-Manuscript.md` (Lines 37, 869) | Precise citation for secondary claim of tertiary elective catheterization non-obstructive yield (30%–50%). | Maintained explicit `[CITATION NEEDED]` tracker for author team to insert their preferred cardiology registry source. |

---

## 8. Required Corrections & Implementation Plan

### Action 1: Replace Institutional Misattribution
- In `CoroVista-Research-Manuscript.md`:
  - Line 17 (Abstract): Replace `Tehran Heart Center` with `Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran)`.
  - Line 83 (Section 1.3): Replace `Tehran Heart Center, Iran` with `Shaheed Rajaei Cardiovascular, Medical and Research Center, Tehran, Iran`.
  - Line 93 (Section 2.1): Replace `at Tehran Heart Center` with `at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran)`.
  - Line 181 (Section 3.1): Replace `Tehran Heart Center, a major tertiary cardiovascular referral and teaching hospital in Tehran, Iran` with `Shaheed Rajaei Cardiovascular, Medical and Research Center, a major tertiary cardiovascular referral and teaching hospital in Tehran, Iran`.
  - Line 187 (Section 3.1): Replace `Tehran Heart Center` with `Shaheed Rajaei Cardiovascular, Medical and Research Center`.
  - Line 773 (Section 6.1): Replace `Tehran Heart Center in Tehran, Iran` with `Shaheed Rajaei Cardiovascular, Medical and Research Center in Tehran, Iran`.
  - Line 820 (Declarations): Replace `Tehran Heart Center` with `Shaheed Rajaei Cardiovascular, Medical and Research Center`.
  - Line 870 (Tracker): Replace `Tehran Heart Center` with `Shaheed Rajaei Cardiovascular, Medical and Research Center`.
- Apply corresponding replacements in `01-*`, `02-*`, `03-*`, `references.md`, and `MANUSCRIPT-EDITORIAL-REVIEW.md` to ensure total workspace consistency.

### Action 2: Insert Missing In-Text Citations
- In `CoroVista-Research-Manuscript.md`:
  - Section 3.3 (Model Selection): Cite `(Pedregosa et al., 2011)` in candidate model architectures and scikit-learn pipeline descriptions.
  - Section 1.3 & Section 3.1: Cite `(Mitsuhashi et al., 2009)` when establishing anatomical vessel partitioning and 3D coronary representations.
  - Section Declarations (Authors' Contributions): Reaffirm `(Mitsuhashi et al., 2009)` in domain asset integration notes.

### Action 3: Refine TRIPOD+AI Compliance Statement
- In Section 1.3, refine Item 7 to state that study reporting was informed by and aligned with the TRIPOD+AI guidelines (Collins et al., 2024).

---

## 9. Unresolved Items & Author-Confirmation Trackers

The following items are legitimately external to repository code and have been properly tagged for the author team:
1. **Formal IRB / Ethics Committee Protocol Identifier:**
   - *Status:* `[UNRESOLVED: Formal IRB/ethics committee protocol number is not recorded in published literature or repository artifacts]`
   - *Action:* The author team may contact Dr. Roohallah Alizadehsani or Dr. Zahra Alizadeh Sani to ascertain if a historical protocol number exists; otherwise, retain the existing waiver declaration for retrospective secondary analysis of open-access de-identified data.
2. **Elective Catheterization Diagnostic Yield Citation:**
   - *Status:* `[CITATION NEEDED]` (Section 1.1)
   - *Action:* Author team can supply their preferred registry citation (e.g., Patel et al., *NEJM* 2010 or 2014 NCDR CathPCI registry) upon final proofing.

---

## 10. Final Publication Readiness Certification

Following the execution of the corrections detailed above:
- **Scientific Integrity:** Verified (Zero data leakage, proper scoring rules, dual SD reporting).
- **Numerical Accuracy:** Verified (100% agreement with locked Phase 5.1 Evidence Matrix).
- **Dataset Provenance:** Verified & Corrected (Accurate institutional origin at Shaheed Rajaei Cardiovascular, Medical and Research Center).
- **Bibliographic Mapping:** Verified (22 of 22 references cited in text and fully resolved).
- **Reporting Quality:** Verified (Meets TRIPOD+AI recommendations for clinical prediction modeling).

**Final Recommendation:** The CoroVista manuscript is declared scientifically verified, editorially validated, and **APPROVED FOR JOURNAL FORMATTING AND PEER REVIEW SUBMISSION**.
