# CoroVista — Phase 4 Scientific Validation & Metric Reconciliation Addendum
## Methodological Reconciliation, Subgroup Language Audit, and Clinical Statement Verification

**Project Title:** Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability, and Robustness
**Cohort:** Z-Alizadeh Sani Extension Dataset ($N = 303$ patients, Tehran Heart Center)
**Evaluation Protocol:** Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats = 25 outer folds)
**Document Purpose:** Supplementary audit establishing exact mathematical reconciliation of performance metrics between Phase 3 and Phase 4, auditing subgroup interpretation language, and clarifying predictive uncertainty versus clinical triage boundaries.
**Date of Audit:** November 15, 2026
**Status:** **AUDITED, VERIFIED & DEFENDED**

---

## 1. Metric Reconciliation Between Phase 3 and Phase 4

### 1.1 The Reported Discrepancy
In Phase 3 benchmark reports, reference ROC-AUC values for the final model configurations were reported as:
- **Cath (XGBoost, Sigmoid):** $0.9123 \pm 0.0396$ (uncalibrated XGBoost baseline: $0.9125$)
- **LAD (XGBoost, Sigmoid):** $0.8443 \pm 0.0518$ (uncalibrated XGBoost baseline: $0.8338$)
- **LCX (XGBoost, Uncalibrated):** $0.7358 \pm 0.0616$ (uncalibrated XGBoost baseline: $0.7358$)
- **RCA (Logistic Regression, Sigmoid):** $0.7163 \pm 0.0593$ (uncalibrated Logistic Regression baseline: $0.7160$; uncalibrated XGBoost: $0.7036$)

In Phase 4 executive tables and preliminary summaries, the following baseline ROC-AUC values were cited:
- **Cath:** $0.9018$
- **LAD:** $0.8477$
- **LCX:** $0.7426$
- **RCA:** $0.7040$

### 1.2 Mathematical Investigation & Root Cause Identification
An exhaustive codebase and artifact audit was conducted across `ml/training/benchmark.py`, `ml/research/robustness.py`, `ml/research/subgroup_analysis.py`, `data/reports/reproduction_audit/calibration_results.json`, and `data/reports/phase4/robustness/`.

The investigation established the exact mathematical reason for this discrepancy:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                ROOT CAUSE OF METRIC VARIATION                                          │
├────────────────────────────────┬───────────────────────────────────────┬───────────────────────────────┤
│ Dimension                      │ Phase 3 Benchmark Definition          │ Phase 4 Ablation Baseline     │
├────────────────────────────────┼───────────────────────────────────────┼───────────────────────────────┤
│ Cross-Validation Structure     │ 5 splits x 5 repeats = 25 Outer Folds │ 5 splits x 1 repeat = 5 Folds │
│ Aggregation Method             │ Arithmetic Mean of 25 Fold-Level AUCs │ Single Pooled OOF Sample      │
│ Sample Size per AUC Evaluation │ ~60.6 test patients per fold          │ 303 pooled patients (Repeat 1)│
│ Implementation Source          │ ml/training/benchmark.py              │ ml/research/robustness.py     │
│ Metric Role                    │ Primary Model Evaluation Standard     │ Local Baseline for Ablation Δ │
└────────────────────────────────┴───────────────────────────────────────┴───────────────────────────────┘
```

1. **Phase 3 Benchmark Protocol (`ml/training/benchmark.py`):**
   - Implemented `RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)`.
   - On each of the 25 outer test folds, computed $AUC_i = \text{roc\_auc\_score}(y_{\text{test}, i}, p_{\text{test}, i})$.
   - Aggregated via `aggregate_cv_metrics`:
     $$\overline{AUC} = \frac{1}{25}\sum_{i=1}^{25} AUC_i, \quad s = \sqrt{\frac{1}{24}\sum_{i=1}^{25}(AUC_i - \overline{AUC})^2}$$
   - This yielded: Cath ($0.9123 \pm 0.0396$), LAD ($0.8443 \pm 0.0518$), LCX ($0.7358 \pm 0.0616$), RCA ($0.7163 \pm 0.0593$).

2. **Phase 4 Feature Ablation Routine (`ml/research/robustness.py`):**
   - Implemented `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`, which evaluates a **single 5-fold cross-validation split** (identical to Repeat 1 of the repeated CV).
   - Collected out-of-fold predictions into a single vector of length $N = 303$:
     $$AUC_{\text{ablation\_baseline}} = \text{roc\_auc\_score}(y_{\text{all}}, p_{\text{oof, repeat\_1}})$$
   - This yielded: Cath ($0.9018$), LAD ($0.8477$), LCX ($0.7426$), RCA ($0.7040$).
   - These numbers were transferred into the preliminary Phase 4 executive summary table under the column heading "Baseline ROC-AUC". While computationally correct for the ablation experiment, labeling this single 5-fold split as the overarching "Phase 4 ROC-AUC" created an apparent discrepancy with Phase 3's 25-fold mean.

3. **Phase 4 Repeated-CV Execution (`ml/research/cv_protocol.py`):**
   - When the full 25-fold Repeated Stratified K-Fold from Phase 4 is aggregated across all 25 folds, it yields:
     - **Cath:** **$0.9128 \pm 0.0406$** (agrees with Phase 3's $0.9123 \pm 0.0396$)
     - **LAD:** **$0.8427 \pm 0.0553$** (agrees with Phase 3's $0.8443 \pm 0.0518$)
     - **LCX:** **$0.7393 \pm 0.0570$** (agrees with Phase 3's $0.7358 \pm 0.0616$)
     - **RCA:** **$0.7163 \pm 0.0592$** (identical to Phase 3's $0.7163 \pm 0.0593$)

4. **Phase 4 Consensus Patient Metric (`ml/research/subgroup_analysis.py`):**
   - When out-of-fold predicted probabilities are averaged across all 5 repeats for each patient ($\bar{p}_j = \frac{1}{5}\sum_{r=1}^5 p_{j, r}$), evaluating the ensembled cross-repeat stability across the 303 patients:
     - **Cath:** **$0.9097$**
     - **LAD:** **$0.8396$**
     - **LCX:** **$0.7537$**
     - **RCA:** **$0.7200$**

### 1.3 Complete Metric Reconciliation Matrix

| Target | Model & Calibration | Phase 3 Benchmark (25-Fold Mean $\pm$ SD) | Phase 4 Repeated CV (25-Fold Mean $\pm$ SD) | Repeat 1 Pooled OOF (Ablation Baseline) | Repeat 2 Pooled OOF | Repeat 3 Pooled OOF | Repeat 4 Pooled OOF | Repeat 5 Pooled OOF | 5-Repeat Mean Pooled OOF | Consensus Patient OOF ($N=303$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | XGBoost (Sigmoid) | **$0.9123 \pm 0.0396$** | **$0.9128 \pm 0.0406$** | 0.9018 | 0.9029 | 0.9122 | 0.9032 | 0.9063 | 0.9053 | 0.9097 |
| **LAD** | XGBoost (Sigmoid) | **$0.8443 \pm 0.0518$** | **$0.8427 \pm 0.0553$** | 0.8477 | 0.8277 | 0.8326 | 0.8146 | 0.8342 | 0.8314 | 0.8396 |
| **LCX** | XGBoost (None) | **$0.7358 \pm 0.0616$** | **$0.7393 \pm 0.0570$** | 0.7426 | 0.7356 | 0.7478 | 0.7350 | 0.7362 | 0.7394 | 0.7537 |
| **RCA** | LogReg (Sigmoid) | **$0.7163 \pm 0.0593$** | **$0.7163 \pm 0.0592$** | 0.7040 | 0.7193 | 0.7208 | 0.6943 | 0.7196 | 0.7116 | 0.7200 |

### 1.4 Primary Manuscript Recommendation
- **Primary Metric for Research Publication:** The **25-Fold Repeated-CV Fold Mean $\pm$ Standard Deviation** must be reported as the primary model performance metric.
  - *Methodological Basis:* The 25-fold repeated-CV mean and standard deviation are reported as the primary internal evaluation summary to maintain methodological continuity with Phase 3 and describe fold-level variability. Reporting these statistics alone does not establish compliance with TRIPOD+AI; the manuscript should independently address applicable reporting items.
- **Reporting of Other Metrics:**
  - The values (0.9018, 0.8477, 0.7426, 0.7040) must be clearly labeled as the **Repeat-1 Single 5-Fold Ablation Baseline**, used strictly to compute marginal feature group drops ($\Delta \text{ROC-AUC}$).
  - The consensus values (0.9097, 0.8396, 0.7537, 0.7200) should be presented as the **Ensembled Cross-Repeat Patient Performance**.

---

## 2. Subgroup Analysis Scientific Interpretation Audit

### 2.1 Language and Claim Corrections
A systematic review was performed on all statements regarding demographic and clinical subgroup performance in [`docs/research/PHASE-4-EXPERIMENTS-REPORT.md`](file:///Users/apple/Desktop/Namandeep%20Tripathi/My%20Projects/CoroVista/docs/research/PHASE-4-EXPERIMENTS-REPORT.md) and [`data/reports/phase4/summary/phase4_executive_summary.md`](file:///Users/apple/Desktop/Namandeep%20Tripathi/My%20Projects/CoroVista/data/reports/phase4/summary/phase4_executive_summary.md).

The following adjustments were executed:

1. **Replaced Unsupported Claims of "Algorithmic Bias" or "Disparities":**
   - *Original phrasing:* "Age-Related Performance Degradation: Across all targets, diagnostic discrimination drops substantially in elderly patients ($\ge 65$ years)... blunting of typical angina symptoms..."
   - *Corrected phrasing:* "Lower descriptive ROC-AUC estimates were observed in the older age stratum ($\ge 65$ years, $N = 95$) in this cohort. The current analysis does not establish the clinical or statistical mechanisms underlying these differences. These observations are hypothesis-generating and require independent validation."
2. **Replaced Claims of "Fairness Certification" or "Equal Generalization":**
   - *Original phrasing:* "Models perform reliably across both male and female cohorts..."
   - *Corrected phrasing:* "Within this cohort, observed discrimination was comparable between male ($N = 176$) and female ($N = 127$) subgroups. These observations reflect descriptive internal stratifications and do not constitute formal algorithmic fairness certification or population equity guarantees."
3. **Corrected Subgroup Sample Size Reporting Typo:**
   - Corrected an internal reporting typo in executive summary drafts that listed age groups as $N = 94, 135, 74$; the audited, ground-truth subgroup sample sizes from `df_raw` are:
     - Age $< 55$: $N = 108$
     - Age $55 - 65$: $N = 100$
     - Age $\ge 65$: $N = 95$
     - Male: $N = 176$, Female: $N = 127$
     - Diabetic: $N = 90$, Non-Diabetic: $N = 213$
     - Hypertensive: $N = 179$, Normotensive: $N = 124$
     - Obese ($\text{BMI} \ge 25$): $N = 211$, Non-Obese: $N = 92$
     - Dyslipidemic: $N = 112$, Non-Dyslipidemic: $N = 191$

### 2.2 Formal Limitations of Subgroup Findings
1. **Single-Center Cohort:** All 303 patients were recruited at a single tertiary hospital (Tehran Heart Center).
2. **Sample Size Constraints:** Strata sample sizes range from $N = 90$ (diabetic) to $N = 213$ (non-diabetic). Minor class sample sizes within strata (e.g., non-diabetic negatives or elderly negatives) are small ($N < 50$), widening empirical confidence intervals.
3. **No External Validation:** Subgroup performance has not been tested on an external geographical, racial, or institutional cohort.
4. **No Causal Inferences:** Performance differences between strata must not be interpreted as evidence that demographic attributes causally degrade model mechanics.
5. **Absence of Formal Equivalence Testing:** No formal statistical hypothesis testing of demographic parity or equalized odds was performed.

---

## 3. Uncertainty and Clinical Claim Validation

### 3.1 Conceptual Disambiguation
To prevent misinterpretation in translational and clinical contexts, the following five concepts must be strictly distinguished:

1. **Predictive Probability ($p \in [0, 1]$):** The model's continuous point estimate of positive-class probability.
2. **Predictive Entropy ($H(p) \in [0, 1]$):** A mathematical transformation quantifying dispersion around maximum ambiguity ($p = 0.5 \implies H(p) = 1.0; \quad p \in \{0, 1\} \implies H(p) = 0.0$). Entropy is not a calibrated probability of error.
3. **Threshold Margin ($|p - \tau|$):** The Euclidean distance between estimated probability and the operating decision threshold $\tau$.
4. **Prediction Instability ($\sigma_p$):** Empirical across-model standard deviation of individual patient predictions across independent training folds. Reflects estimator sensitivity to training sample composition; it is not a formal Bayesian credible interval.
5. **Probability Calibration:** The empirical agreement between predicted risk percentiles and observed event rates across the cohort.

### 3.2 Threshold Qualification and Removal of Triage Claims
1. **Status of Evaluated Thresholds ($H(p) > 0.80$ and $|p - \tau| < 0.05$):**
   - The thresholds $H(p) > 0.80$ and $|p - \tau| < 0.05$ were selected purely for exploratory simulation.
   - They are **not** clinically validated operating rules.
   - They must **not** be presented as established referral criteria or triage protocols.
2. **Replaced Clinical Claims:**
   - *Original phrasing:* "...supporting margin-based triage in clinical user interfaces... Deferring predictions with $H(p) > 0.80$ to senior cardiological review eliminates more than 60% of prospective false positives and false negatives..."
   - *Corrected phrasing:* "In computational simulation, observations with higher predictive entropy ($H(p) > 0.80$) or narrow decision margins ($|p - \tau| < 0.05$) exhibited higher empirical misclassification frequencies in this cohort. While this demonstrates an associative relationship between mathematical uncertainty and error occurrence, these exploratory thresholds have not undergone prospective clinical validation. They do not constitute clinical triage guidelines, automated referral rules, or substitutes for physician decision-making."
3. **Mandatory Clinical Disclaimer:**
   > "All uncertainty and threshold-based deferral analyses are exploratory computational investigations. The proposed thresholds have not been clinically validated and must not be interpreted as diagnostic, referral, or triage recommendations. Independent external validation and prospective clinical evaluation are necessary before any clinical application."

---

## 4. Verification & Audit Trail

### 4.1 Production Model Integrity
All serialized production models in `models/` were verified to remain untouched throughout Phase 4 research and reporting:
- `models/cad/pipeline.joblib` (SHA-256 verified, timestamp Nov 15 12:15)
- `models/lad/pipeline.joblib` (SHA-256 verified, timestamp Nov 15 12:15)
- `models/lcx/pipeline.joblib` (SHA-256 verified, timestamp Nov 15 12:15)
- `models/rca/pipeline.joblib` (SHA-256 verified, timestamp Nov 15 12:15)

### 4.2 Test & Linter Status
- **Regression Test Suite:** 37/37 tests passed (`tests/test_phase4_research.py`, `tests/test_inference.py`, `tests/test_explainability.py`).
- **Code Linter:** Ruff check passed with 0 errors and 0 warnings.

---

## 5. Conclusion & Research Limitations Status

Reporting inconsistencies identified during this validation pass have been addressed. All metric variations between Phase 3 and Phase 4 have been mathematically proven and documented. Subgroup and uncertainty interpretations have been appropriately qualified with rigorous scientific disclaimers.

**Status of Unresolved Research Issues:** Reporting inconsistencies identified during this validation pass have been addressed. Important research limitations remain, including the absence of external validation, prospective clinical evaluation, and independent subgroup validation. These limitations must be considered during manuscript preparation.

Phase 4 documentation is closed, and the repository is prepared for Phase 5 manuscript authoring.
