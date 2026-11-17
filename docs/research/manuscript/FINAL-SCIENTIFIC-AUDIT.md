# CoroVista — Final Scientific Audit & Submission-Readiness Review

**Manuscript Title:** Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness
**Date of Audit:** November 17, 2026
**Repository Branch:** `development`
**Primary Manuscript File:** [`docs/research/manuscript/CoroVista-Research-Manuscript.md`](file:///Users/apple/Desktop/Namandeep%20Tripathi/My%20Projects/CoroVista/docs/research/manuscript/CoroVista-Research-Manuscript.md)
**Readiness Assessment Classification:** **Scientifically consistent — pending external administrative requirements**

---

## 1. Executive Summary

This audit report documents the comprehensive, targeted scientific correction, numerical verification, and submission-readiness review of the final approved CoroVista research manuscript. The manuscript has been authored and approved under the confirmed dual-authorship arrangement (Naman Deep Tripathi, First & Corresponding Author; Nikhil Agrawal, Co-Author).

All scientific corrections mandated by the pre-submission consistency audit have been applied across the master manuscript (`CoroVista-Research-Manuscript.md`), its constituent modular drafts (`01-...`, `02-...`, `03-...`, `references.md`), and the editorial review records (`MANUSCRIPT-EDITORIAL-REVIEW.md`). Every empirical claim, metric distribution, operating threshold, and uncertainty parameter was audited against raw serialized benchmark artifacts (`data/reports/phase4/summary/phase4_master_metrics.json`, `models/rca/metadata.json`, and `data/reports/reproduction_audit/calibration_results.json`).

The manuscript is **scientifically consistent, numerically reconciled, and free of unsupported causal or translational claims**, pending only external administrative requirements (target journal ethics policy confirmation and portal-specific departmental metadata).

---

## 2. Mandatory Scientific Corrections Implemented

### A. Prediction Stability: Boundary-Flip Claim Correction
- **Original Deficiency:** Preliminary draft phrasing suggested or implied that 100% of patients across all prediction targets experienced classification flips within the immediate decision-boundary margin ($|p - \tau| < 0.05$).
- **Verified Empirical Evidence (Exp B, Table 8):**
  - **Cath ($\tau = 0.50$):** 6 patients in $|p - \tau| < 0.05$; $0.0\%$ invariance ($0/6$ invariant; $6/6$ flipped across 5 repeats).
  - **LAD ($\tau = 0.50$):** 17 patients in $|p - \tau| < 0.05$; $0.0\%$ invariance ($0/17$ invariant; $17/17$ flipped across 5 repeats).
  - **LCX ($\tau = 0.50$):** 45 patients in $|p - \tau| < 0.05$; $2.2\%$ invariance ($1/45$ invariant; $44/45$ flipped across 5 repeats).
  - **RCA ($\tau = 0.35$):** 75 patients in $|p - \tau| < 0.05$; $22.7\%$ invariance ($17/75$ invariant; $58/75$ flipped across 5 repeats).
- **Corrected Scientific Interpretation:**
  - In the immediate boundary group, all Cath and LAD patients experienced at least one label change across 5 repeats ($0\%$ invariance).
  - Neither LCX ($2.2\%$ invariance, $44/45$ flipped) nor RCA ($22.7\%$ invariance, $58/75$ flipped) exhibited a 100% flip rate.
  - Predictions closer to operating thresholds were generally less stable without implying that every near-boundary patient across all vessels necessarily flips.
  - Confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance across all targets (Cath $244/246$, LAD $190/190$, LCX $135/136$, RCA $48/48$).
- **Audit Scope:** Applied across Abstract, Contributions (Section 1.3), Results (Section 4.5, Table 8), Figure 4 caption (Section 4.9), Discussion (Section 5.5), and Conclusion (Section 7.1).

### B. Predictive Entropy: Ground-Truth Distinction Correction
- **Original Deficiency:** Draft text asserted or implied that normalized predictive entropy autonomously "detects errors without ground-truth labels."
- **Verified Methodological Distinction:**
  - Normalized binary predictive entropy $H(p) = -p \log_2(p) - (1-p) \log_2(1-p)$ can be computed directly from model output probabilities without access to ground-truth outcome labels at inference time.
  - However, evaluating whether entropy discriminates correct from incorrect classifications fundamentally requires reference ground-truth catheterization labels.
  - The reported error-detection ROC-AUC values (Cath $0.7593$, LAD $0.6595$, LCX $0.6392$, RCA $0.6796$) represent **retrospective evaluation metrics**, not autonomous label-free clinical error detectors in live deployment.
- **Audit Scope:** Applied across Abstract, Contributions (Section 1.3), Methods (Section 3.7), Results (Section 4.6, Table 9), Figure 5 caption (Section 4.9), Discussion (Section 5.6), and Conclusion (Section 7.1).

### C. TRIPOD+AI Reporting Language Qualification
- **Original Deficiency:** Early text contained assertive phrasing such as "In strict accordance with the TRIPOD+AI guidelines."
- **Corrected Standard:**
  - Softened to: *"Reporting was informed by the TRIPOD+AI recommendations (Collins et al., 2024)."*
  - Explicitly declared in Section 1.3 and Section 6.2 that formal checklist-based compliance certification remains outside the scope of this retrospective computational study.
- **Audit Scope:** Section 1.3 (Contribution 7), Section 3.2 (Pipeline), Section 6.2 (Limitations), and related front-matter descriptions.

### D. Clinical Claim Qualifications & Conservatism
- **LAD Stenosis & Revascularization (Section 1.1 & Section 5.1):** Replaced assertive clinical directive language with qualified guideline-referenced text: revascularization is frequently prioritized under clinical practice guidelines for eligible symptomatic or high-risk patients (Lawton et al., 2022).
- **Coronary Territory Physiological Explanations (Section 5.1 & Section 5.7):** Explicitly qualified observational model associations versus causal biological mechanisms. Observational machine learning correlations do not establish causal biology or interventional targets. Replaced "clinical dogma" with "established clinical consensus".
- **Operating Cutoffs & Threshold Disclaimers (Section 5.3 & Section 6.7):** Explicitly clarified that inner-fold tuned cutoffs ($0.3188$) and fixed production cutoffs ($\tau = 0.35$) are exploratory research operating points for statistical trade-off optimization in this dataset, not clinically validated diagnostic criteria or treatment thresholds.
- **Defensive Uncertainty Flagging (Section 5.6):** Reframed entropy and decision margin distance as exploratory algorithmic safety indicators, rather than validated clinical triage rules.

---

## 3. Comprehensive Numerical Audit Matrix

Every empirical value in the manuscript was checked against raw experiment outputs:

| Benchmark Dimension | Verified Value in Code & Artifacts | Manuscript Value & Location | Status |
| :--- | :--- | :--- | :--- |
| **Cohort Size** | $N = 303$ consecutive patients | $N = 303$ (Sections 1.3, 3.1, Table 1) | **VERIFIED** |
| **Raw Column Count** | 59 columns in source spreadsheet | 59 columns (Section 3.2) | **VERIFIED** |
| **Prediction Targets** | 4 targets (`Cath`, `LAD`, `LCX`, `RCA`) | 4 targets (Section 3.1, Section 4.1) | **VERIFIED** |
| **Active Feature Space** | 54 predictive features (1 zero-variance dropped) | 54 features (Section 3.2) | **VERIFIED** |
| **Transformed Design Matrix** | 57 numerical dimensions ($22 + 28 + 7$) | 57 dimensions (Section 3.2) | **VERIFIED** |
| **Target Prevalence: Cath** | Positive $216$ ($71.29\%$), Negative $87$ ($28.71\%$) | $71.29\%$ (Sections 3.1, 4.1, Table 1) | **VERIFIED** |
| **Target Prevalence: LAD** | Positive $177$ ($58.42\%$), Negative $126$ ($41.58\%$) | $58.42\%$ (Sections 3.1, 4.1, Table 1) | **VERIFIED** |
| **Target Prevalence: LCX** | Positive $119$ ($39.27\%$), Negative $184$ ($60.73\%$) | $39.27\%$ (Sections 3.1, 4.1, Table 1) | **VERIFIED** |
| **Target Prevalence: RCA** | Positive $114$ ($37.62\%$), Negative $189$ ($62.38\%$) | $37.62\%$ (Sections 3.1, 4.1, Table 1) | **VERIFIED** |
| **Anatomical Discordance** | Index 93 (LAD Stenotic, Cath Normal) preserved | Fully documented in Section 3.1 & Table 1 | **VERIFIED** |
| **Evaluation Scheme** | 25-fold Repeated Stratified CV ($5 \times 5$) | 25 folds (Section 3.3, Section 3.5) | **VERIFIED** |
| **Selected Model: Cath** | XGBoost + Sigmoid Platt | ROC-AUC $0.9123 \pm 0.0404$, Brier $0.1034$, ECE $0.1004$ (Table 2) | **VERIFIED** |
| **Selected Model: LAD** | XGBoost + Sigmoid Platt | ROC-AUC $0.8443 \pm 0.0528$, Brier $0.1609$, ECE $0.1326$ (Table 2) | **VERIFIED** |
| **Selected Model: LCX** | XGBoost Uncalibrated | ROC-AUC $0.7358 \pm 0.0629$, Brier $0.2054$, ECE $0.1366$ (Table 2) | **VERIFIED** |
| **Selected Model: RCA** | Logistic Regression + Sigmoid Platt | ROC-AUC $0.7163 \pm 0.0605$, Brier $0.2060$, ECE $0.1000$ (Table 2) | **VERIFIED** |
| **RCA Standard Midpoint ($\tau = 0.50$)** | Sensitivity $31.24\% \pm 8.56\%$, Specificity $86.38\%$ | Sensitivity collapse documented in Table 4, Section 5.3 | **VERIFIED** |
| **RCA Tuned Cutoff Mean** | Mean $0.3188$, Range $[0.20, 0.37]$ | Mean $0.3188$ (Table 5, Section 4.3, Section 5.3) | **VERIFIED** |
| **RCA Tuned Cutoff Sample SD** | Sample SD $= 0.0380$ (`ddof=1`) | Locked as **$0.0380$**; legacy $0.0388$ retired (Table 5 note) | **VERIFIED** |
| **RCA Tuned Cutoff Pop SD** | Population SD $= 0.0372$ (`ddof=0`) | Documented as $0.0372$ (Table 5 note, Section 3.5) | **VERIFIED** |
| **RCA Tuned Performance** | Sensitivity $79.46\% \pm 10.92\%$, BalAcc $64.43\%$ | $79.46\%$ sensitivity, $F_1 = 0.6037$ (Table 5) | **VERIFIED** |
| **RCA Production Cutoff $\tau = 0.35$ (Folds)** | Sensitivity $74.21\% \pm 10.64\%$, Spec $57.48\%$ | Documented across 25 outer folds (Table 6) | **VERIFIED** |
| **RCA Production Cutoff $\tau = 0.35$ (Repeats)**| Sensitivity $74.21\% \pm 2.53\%$, Spec $57.46\%$ | Documented across 5 complete repeats (Table 6) | **VERIFIED** |
| **SHAP Additivity Verification** | Additivity error $< 1.2 \times 10^{-6}$ in 25/25 folds | 100% additivity pass verified (Section 4.4, Table 7) | **VERIFIED** |
| **SHAP Rank Stability (Spearman $\rho$)** | Cath $0.9319$, LAD $0.9217$, LCX $0.9081$, RCA $0.7737$ | Mean $\rho$ across 300 fold pairs (Table 7) | **VERIFIED** |
| **LAD Top-5 Jaccard Similarity** | $0.7456 \pm 0.1417$; 4 features in 100% folds | Age, EF, RWMA, Typical CP in 25/25 folds (Table 7) | **VERIFIED** |
| **Prediction Flips Across 5 Repeats** | Cath $27/303$ ($8.91\%$), LAD $55/303$ ($18.15\%$) | LCX $100/303$ ($33.00\%$), RCA $74/303$ ($24.42\%$) (Table 8) | **VERIFIED** |
| **Boundary Invariance ($|p - \tau| < 0.05$)** | Cath $0/6$ ($0\%$), LAD $0/17$ ($0\%$) | LCX $1/45$ ($2.2\%$), RCA $17/75$ ($22.7\%$) (Table 8) | **VERIFIED** |
| **Distant Invariance ($|p - \tau| \ge 0.20$)** | Cath $244/246$ ($99.2\%$), LAD $190/190$ ($100\%$) | LCX $135/136$ ($99.3\%$), RCA $48/48$ ($100\%$) (Table 8) | **VERIFIED** |
| **Retrospective Entropy ROC-AUC** | Cath $0.7593$, LAD $0.6595$, LCX $0.6392$, RCA $0.6796$ | Documented as retrospective evaluation (Table 9, Section 4.6) | **VERIFIED** |
| **Cath Error Rates by Margin** | Margin $<0.05$: $33.3\% \to$ Margin $\ge 0.20$: $1.6\%$ | Monotonic gradient documented (Table 9, Section 5.6) | **VERIFIED** |
| **Feature Ablation Impact: Symptoms** | Cath $\Delta = -0.0847$, LAD $\Delta = -0.0532$ | Retrained inside 5-fold CV (Table 11, Section 4.7) | **VERIFIED** |
| **Feature Ablation Impact: Echo** | LAD $\Delta = -0.0528$ (Echo is primary LAD anchor) | LCX $\Delta = -0.0185$, RCA $\Delta = -0.0094$ (Table 11) | **VERIFIED** |
| **Feature Ablation Impact: Lab Panel** | LCX $\Delta = -0.0524$ (Labs compensate for LCX) | LAD $\Delta = -0.0189$, Cath $\Delta = -0.0142$ (Table 11) | **VERIFIED** |
| **Exploratory Subgroups** | 13 feasible strata ($N \ge 30, \min(N_+, N_-) \ge 5$) | Feasibility guard enforced (Table 12, Section 4.8) | **VERIFIED** |
| **Elderly Attenuation (Age $\ge 65$)** | Cath ROC-AUC $0.7480$ vs younger $0.8954$ | Exploratory hypothesis documented (Table 12, Section 6.6) | **VERIFIED** |

---

## 4. Citation and Literature Verification

1. **Elective Catheterization Diagnostic Yield Citation:**
   - The reference standard for non-obstructive catheterization yield is verified as:
     **Patel, M. R., Peterson, E. D., Dai, D., Brennan, J. M., Redberg, R. F., Anderson, H. V., Brindis, R. G., & Douglas, P. S. (2010). Low diagnostic yield of elective coronary angiography. *New England Journal of Medicine*, 362(10), 886–895. DOI: [10.1056/NEJMoa0907272](https://doi.org/10.1056/NEJMoa0907272)**
   - Embedded in Section 1.1 (line 36) and in bibliography entry 14.
2. **Ethics Protocol Absence Transparency:**
   - In accordance with research integrity standards, the absence of an institutional ethics approval protocol identifier from the original 2011–2013 clinical data collection at Shaheed Rajaei Cardiovascular Center is transparently stated. No historical protocol number has been fabricated.
3. **Absence of Unresolved Citation Tags:**
   - A global repository search confirmed **zero unverified claims or unresolved `[CITATION NEEDED]` tags** in the manuscript prose.

---

## 5. Ethics Determination & Data Governance Review

1. **Dataset Provenance:**
   - The study utilizes previously published, fully de-identified, publicly accessible tabular research data from the extended Z-Alizadeh Sani coronary artery disease dataset (UCI Machine Learning Repository DOI: 10.24432/C5Q31T; Mendeley Data DOI: 10.17632/9k56pwtvz9.1).
2. **Secondary Computational Analysis:**
   - The current study represents an independent secondary computational modeling investigation. It involved no prospective patient recruitment, clinical trials, healthcare interventions, biological sample collection, or patient re-identification potential.
3. **No Fabrication of Ethics Approvals:**
   - In strict compliance with research ethics, no IRB approval number, ethics committee waiver certificate, or institutional determination has been fabricated, assumed, or falsely claimed.
4. **Ethics Determination Status:**
   - The manuscript text (Section 3.1 and Declarations) explicitly affirms that **public availability of open data does not automatically obviate institutional research ethics governance**. Because an independent institutional ethics review determination or formal waiver has not been independently documented for this secondary study, the formal determination remains to be confirmed with the target journal or relevant institutional ethics body.
   - **Formal ethics clearance is explicitly NOT marked as completed.**

---

## 6. Author Metadata & Submission Sign-Off Verification

The dual-authorship arrangement (Option A) has been verified and confirmed across all submission artifacts:

1. **Author 1 — First and Corresponding Author:**
   - **Name:** Naman Deep Tripathi
   - **Academic Status:** Bachelor of Computer Applications (BCA), Second Year
   - **Institution:** Sanskriti University
   - **Location:** Mathura, Uttar Pradesh, India
   - **Email:** `namandeeptripathi@gmail.com`
   - **ORCID:** [0009-0006-8775-3794](https://orcid.org/0009-0006-8775-3794)
   - **Role:** Corresponding Author
   - **CRediT Contributions:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing – original draft, Writing – review and editing.
   - **Status:** Final manuscript approved; dual authorship confirmed.
2. **Author 2 — Co-Author:**
   - **Name:** Nikhil Agrawal
   - **Academic Status:** Bachelor of Technology (B.Tech.), Fourth Year
   - **Institution:** VIT Bhopal University
   - **Location:** Bhopal, Madhya Pradesh, India
   - **Email:** `agnikhil9897@gmail.com`
   - **ORCID:** [0009-0009-1546-5576](https://orcid.org/0009-0009-1546-5576)
   - **Role:** Co-Author
   - **CRediT Contributions:** Cardiovascular domain mapping, Anatomical multi-target localization, 3D anatomical asset integration, Clinical workflow visualization, Early data exploration and data audit, Critical manuscript review.
   - **Status:** Final manuscript approved; dual authorship confirmed.
3. **Affiliation Notes:**
   - Specific internal departments within Sanskriti University and VIT Bhopal University have not been provided or guessed; they are explicitly flagged for author confirmation during journal portal entry if required.

---

## 7. Remaining External Administrative Requirements

While all scientific and internal editorial requirements are fully resolved, the following administrative items remain pending external confirmation:
1. **Target Journal Ethics Policy Determination:** The journal editorial office (*Computers in Biology and Medicine* or alternative target) must confirm whether secondary computational analysis of publicly available de-identified open data requires a formal institutional exemption certificate or is accepted under standard open-data editorial policies.
2. **Portal Department Confirmation:** Authors must select their respective departmental affiliations in the Elsevier Editorial Manager portal if mandatory dropdown fields require departmental designation.
3. **Publishing Model Confirmation:** Standard subscription publishing route is confirmed as preferred, subject to final journal licensing verification upon acceptance.

---

## 8. Final Readiness Assessment

**Final Classification:**
### **Scientifically consistent — pending external administrative requirements**

- **Scientific Depth & Technical Accuracy:** Fully validated against all repository code, pipelines, and experiment artifacts.
- **Reporting Standards:** Meticulously aligned with principles emphasized by TRIPOD+AI recommendations.
- **Transparency & Integrity:** Transparent data governance, qualified clinical claims, no fabricated numbers or credentials, and exact cross-document consistency.
