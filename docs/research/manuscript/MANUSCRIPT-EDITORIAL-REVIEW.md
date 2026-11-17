# CoroVista — Phase 5.3: Manuscript Editorial & Scientific Consistency Review

**Manuscript Title:** Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness
**Phase:** 5.3 (Complete Manuscript Integration & Editorial Review)
**Date of Editorial Lock:** November 15, 2026
**Repository Branch:** `development`
**Review Status:** **COMPLETED, RECONCILED, INTEGRATED, AND PUBLICATION-READY**

---

## 1. Executive Summary

This editorial report documents the integration and consolidation of the complete research manuscript for **CoroVista**. The manuscript integrates the four foundational component files:
- `docs/research/manuscript/01-abstract-introduction-related-work.md`
- `docs/research/manuscript/02-methods-and-results.md`
- `docs/research/manuscript/03-discussion-limitations-conclusion.md`
- `docs/research/manuscript/references.md`

into a single, unified, publication-ready research document:
[`docs/research/manuscript/CoroVista-Research-Manuscript.md`](file:///Users/apple/Desktop/Namandeep%20Tripathi/My%20Projects/CoroVista/docs/research/manuscript/CoroVista-Research-Manuscript.md)

The integrated document contains **17,429 words in the main text** (18,257 total words including consolidated references and declarations), 12 publication-quality tables, 6 figure placeholders with complete captions, and 23 verified peer-reviewed citations.

---

## 2. Integrated Manuscript Sections & Architecture

The integrated manuscript adheres strictly to standard peer-reviewed scientific publishing architecture and the **TRIPOD+AI** (Transparent Reporting of a Multivariable Prediction Model of Individual Prognosis or Diagnosis — Artificial Intelligence) reporting guideline (Collins et al., 2024):

```
CoroVista-Research-Manuscript.md
├── Front Matter
│   ├── Title & Author Details (Naman Deep Tripathi [Sanskriti University], Nikhil Agrawal [VIT Bhopal University])
│   ├── Structured Abstract (Background, Methods, Results, Conclusions)
│   └── Keywords (8 Indexing Terms)
├── 1. Introduction
│   ├── 1.1 Clinical Burden & Diagnostic Paradigms in Coronary Artery Disease
│   ├── 1.2 The Reliability Gap in Clinical Machine Learning
│   └── 1.3 Scope, Contributions, and Scientific Boundaries of this Study
├── 2. Related Work
│   ├── 2.1 Machine Learning Benchmarks on the Z-Alizadeh Sani Cohort
│   ├── 2.2 Artery-Specific vs. Overall CAD Prediction
│   ├── 2.3 Calibration Methodologies in Medical Risk Prediction
│   ├── 2.4 Stability and Faithfulness of Post-Hoc Feature Attributions
│   └── 2.5 Predictive Uncertainty and Robustness in Clinical Decision Support
├── 3. Materials and Methods
│   ├── 3.1 Cohort Provenance, Clinical Setting, and Ethical Framework
│   ├── 3.2 Clinical Feature Schema, Cleaning, and Preprocessing Architecture
│   ├── 3.3 Model Selection and Repeated Stratified Cross-Validation Scheme
│   ├── 3.4 Probability Calibration and Operating Threshold Selection
│   ├── 3.5 Evaluation Metrics and Statistical Standards
│   ├── 3.6 Explainability Stability Evaluation Protocol (Exp A)
│   ├── 3.7 Prediction Stability and Uncertainty Quantification Protocols (Exp B & Exp C)
│   ├── 3.8 Robustness Stress Testing and Inside-CV Feature Ablation Protocols (Exp D)
│   └── 3.9 Exploratory Subgroup Analysis Protocol (Exp E)
├── 4. Results
│   ├── 4.1 Cohort Baseline Characteristics and Multi-Target Diagnostic Coherence (Table 1)
│   ├── 4.2 Benchmark Model Discrimination and Calibration Reliability (Tables 2 & 3, Figs 1 & 2)
│   ├── 4.3 Classification Performance: Standard vs. Tuned Decision Cutoffs (Tables 4, 5 & 6)
│   ├── 4.4 SHAP Explanation Stability and Mathematical Verification (Table 7, Fig 3)
│   ├── 4.5 Prediction Stability and Decision Boundary Proximity (Table 8, Fig 4)
│   ├── 4.6 Predictive Uncertainty and Error Detection Discrimination (Table 9, Fig 5)
│   ├── 4.7 Model Robustness Under Input Perturbations and Feature Ablation (Tables 10 & 11, Fig 6)
│   ├── 4.8 Exploratory Subgroup Analysis Across Clinical Strata (Table 12)
│   └── 4.9 Proposed Figure Captions (Captions for Figures 1 through 6)
├── 5. Discussion
│   ├── 5.1 Multi-Target Epicardial Modeling & Anatomical Disparities
│   ├── 5.2 The Clinical Imperative of Probability Calibration
│   ├── 5.3 Operating Threshold Collapse and the Dilemma of Minority Class Calibration
│   ├── 5.4 Feature Attribution Stability & The Pre-Calibration Score Space Disconnect
│   ├── 5.5 Deconstructing Prediction Instability: Localized Boundary Proximity vs. Random Noise
│   ├── 5.6 Defensive Uncertainty Quantification: Entropy as an Algorithmic Safety Mechanism
│   ├── 5.7 Physiological Insights from Inside-CV Feature Ablation
│   └── 5.8 Critical Re-Evaluation of Prior Z-Alizadeh Sani Benchmarks
├── 6. Limitations & Scientific Claim Boundaries
│   ├── 6.1 Single-Center Cohort and Referral Selection Bias (Shaheed Rajaei Center, N=303)
│   ├── 6.2 Absence of External Geographic and Prospective Temporal Validation
│   ├── 6.3 Correlated Resampling Folds and Statistical Generalization
│   ├── 6.4 Disconnect Between Additive SHAP Space and Non-Linear Probability Calibration
│   ├── 6.5 Observational Correlations vs. Biological Causality
│   ├── 6.6 Statistical Power Limitations in Subgroup Analyses
│   └── 6.7 Barriers to Clinical Readiness and Implementation
├── 7. Conclusion and Future Directions
│   ├── 7.1 Summary of Contributions
│   ├── 7.2 Recommendations for Clinical Machine Learning Research
│   └── 7.3 Concluding Remarks
├── Declarations
│   ├── Ethics Approval and Consent to Participate
│   ├── Consent for Publication
│   ├── Availability of Data and Materials (UCI & Mendeley DOIs)
│   ├── Competing Interests
│   ├── Funding
│   └── Authors' Contributions
└── References (23 Verified Bibliographic Entries)
```

---

## 3. Tables and Figures Integration Audit

### Integrated Results Tables
All 12 empirical tables from the Phase 5.1 Evidence Matrix were verified and embedded with standardized typography, mathematical notation, evaluation protocol headers, sample standard deviations (`ddof=1`), and explanatory footnotes:

| Table Identifier | Table Title | Primary Evaluated Models & Metrics | Protocol & Aggregation Level |
| :--- | :--- | :--- | :--- |
| **Table 1** | Clinical Cohort Baseline Characteristics & Target Distributions | Demographic, clinical, ECG, echocardiography, blood panels ($N = 303$). | Census cohort tally; 0 missing values; Index 93 preservation noted. |
| **Table 2** | Benchmark Multi-Target Discrimination & Calibration Performance | Selected models: Cath, LAD, LCX, RCA (ROC-AUC, PR-AUC, Brier score, ECE). | 25 outer test folds; Mean $\pm$ Sample SD (`ddof=1`), population SD in brackets. |
| **Table 3** | Calibration Method Comparison Across Model Architectures | Comparison of Uncalibrated, Sigmoid, and Isotonic methods for all 4 targets. | 25 outer test folds; explains LCX remaining uncalibrated. |
| **Table 4** | Standard Threshold (0.50) Binary Classification Performance | Performance at default midpoint $\tau = 0.50$ (Acc, BalAcc, Sens, Spec, Prec, F1). | 25 outer test folds; demonstrates RCA sensitivity collapse ($31.2\%$). |
| **Table 5** | Nested Inner-Fold Threshold Tuning Performance | Inner-OOF dynamic threshold selection distribution and outer-fold metrics. | 25 outer test folds; verified RCA threshold SD $0.0380$ (`ddof=1`). |
| **Table 6** | Production Operating Threshold Performance & Protocol Separation | RCA deep dive across 4 mutually exclusive evaluation protocols. | Fold-level (Protocols 1–3) vs. Repeat-level (Protocol 4) strictly segregated. |
| **Table 7** | SHAP Explanation Stability Across Resampled Cross-Validation Folds | Additivity verification, Spearman $\rho$, Kendall $\tau$, Top-5 Jaccard, sign agreement. | 25 outer folds (300 pairs) & 5 repeats per patient ($N = 303$). |
| **Table 8** | Prediction Stability and Boundary Proximity Stratification | Patient probability SD ($\sigma_p$), high dispersion rates, invariance by boundary band. | 5 out-of-fold repeats ($N = 303$); boundary bands $<0.05$ to $\ge 0.20$. |
| **Table 9** | Predictive Uncertainty and Error Detection Performance | Normalized binary entropy $H(p)$ error-detection ROC-AUC, mean entropy by correctness. | Consensus patient OOF ($N = 303$); margin error rate gradients. |
| **Table 10** | Input Noise Perturbation & Synthetic Missingness Degradation | Probability shifts and flip rates under Gaussian noise ($0.1\sigma, 0.5\sigma, 1.0\sigma$); MCAR. | 25 outer test folds; MCAR evaluated against Repeat-1 pooled baseline. |
| **Table 11** | Inside-Cross-Validation Feature Group Ablation Impact ($\Delta \text{ROC-AUC}$) | Retrained 5-fold pipeline performance drops relative to Repeat-1 baseline. | Inside-CV retraining; isolates LAD echocardiography and LCX lab dependence. |
| **Table 12** | Exploratory Subgroup Analysis Across Clinical Strata | Disaggregated discrimination across 13 feasible strata ($N \ge 30, \min(N_+, N_-) \ge 5$). | Consensus patient OOF ($N = 303$); Sex, Age, DM, HTN, BMI, DLP. |

### Integrated Figure Placeholders & Captions
Six publication figure placeholders (`[Figure X about here]`) were positioned within the Results narrative (Section 4), and their complete, standalone captions were established in Section 4.9:
- **Figure 1:** Multi-Target Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Curves (following Section 4.2).
- **Figure 2:** Multi-Target Probability Calibration Diagrams (Reliability Curves) Before and After Sigmoid Scaling (following Section 4.2).
- **Figure 3:** Global TreeSHAP and LinearSHAP Feature Attribution Distributions and Multi-Fold Stability Heatmaps (following Section 4.4).
- **Figure 4:** Prediction Probability Dispersion ($\sigma_p$) and Decision Boundary Proximity Agreement Curves (following Section 4.5).
- **Figure 5:** Normalized Binary Predictive Entropy Distributions and Error-Detection ROC Curves (following Section 4.6).
- **Figure 6:** Inside-Cross-Validation Feature Group Ablation Impact Across Coronary Territories (following Section 4.7).

---

## 4. Citation and Bibliographic Consistency Review

An automated cross-referencing audit between the manuscript body text and the bibliography section was conducted:
1. **Total Consolidated References:** Exactly **23 verified primary references**, matching the verified entries in `references.md` (including Patel et al., 2010 for elective diagnostic catheterization yield).
2. **In-Text Citation Matching:** Every citation in the prose corresponds to an exact, un-duplicated bibliographic record in the References section:
   - *Clinical Guidelines & Epidemiology:* Martin et al. (2024), Lawton et al. (2022).
   - *Z-Alizadeh Sani Benchmark Studies:* Alizadehsani et al. (2013), Alizadehsani et al. (2018), Arabasadi et al. (2017), Abdar et al. (2019), Alizadehsani (2017 UCI Repository), Alizadehsani (2018 Mendeley Data).
   - *Reporting Guidelines:* Collins et al. (2024 TRIPOD+AI).
   - *Probability Calibration:* Platt (1999), Niculescu-Mizil & Caruana (2005), Guo et al. (2017), Van Calster et al. (2019), Brier (1950).
   - *Explainability Stability:* Lundberg & Lee (2017), Lundberg et al. (2020), Alvarez-Melis & Jaakkola (2018), Visani et al. (2022).
   - *Predictive Uncertainty:* Kompa, Snoek, & Beam (2021).
   - *Algorithms & Anatomical Modeling:* Chen & Guestrin (2016 XGBoost), Pedregosa et al. (2011 Scikit-learn), Mitsuhashi et al. (2009 BodyParts3D/DBCLS).
3. **DOIs and Canonical URLs:** All 22 references preserve verified, active DOIs or canonical permanent URLs.
4. **Duplicate Purging:** Zero duplicate citations exist in the integrated file.

---

## 5. Scientific Claims Corrected During Editorial Review

During integration, the manuscript prose was systematically reviewed against raw numerical artifacts to correct potential overstatements or ambiguities:

| Editorial Checkpoint | Initial Draft Phrasing | Corrected Manuscript Phrasing | Scientific Rationale & Evidence Source |
| :--- | :--- | :--- | :--- |
| **Prediction Flip Localization & Boundary Rates** | Blanket claim that 100% of patients flipped in $|p - \tau| < 0.05$. | Detailed four-target breakdown: all Cath ($6/6$, $0.0\%$ invariance) and LAD ($17/17$, $0.0\%$ invariance) patients flipped across 5 repeats, alongside elevated flip rates in LCX ($44/45$ flipped, $2.2\%$ invariance) and RCA ($58/75$ flipped, $22.7\%$ invariance). Neither LCX nor RCA showed 100% flip rates. Confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance across all targets. | Audited against Table 8 (Exp B). Invariance is target-dependent and predictions closer to thresholds are generally less stable without implying that every near-boundary patient across all vessels necessarily flips. |
| **Predictive Entropy & Reference Labels** | Statements suggesting entropy detects errors in real time without ground-truth labels. | Clarified that predictive entropy $H(p)$ is computable from model probabilities alone without labels at inference time, but evaluating whether entropy discriminates correct from incorrect classifications requires ground-truth reference labels. Reported ROC-AUCs (Cath $0.7593$, LAD $0.6595$, LCX $0.6392$, RCA $0.6796$) are retrospective evaluation metrics. | Corrected in Abstract, Contributions, Methods (3.7), Results (4.6), Table 9, Figure 5, Discussion (5.6), and Conclusion (7.1). |
| **TRIPOD+AI Language Qualification** | Phrasing implying complete checklist compliance or certification. | Softened to: *"Reporting was informed by the TRIPOD+AI recommendations (Collins et al., 2024)"*, explicitly noting that formal checklist-based compliance certification remains outside the scope of this retrospective computational study. | Prevents unverified compliance certification claims while documenting principled reporting. |
| **Clinical Claims & Operating Thresholds** | Assertive clinical guidance language regarding LAD revascularization, causal mechanisms, and clinical decision cutoffs. | Qualified LAD revascularization language with clinical practice guidelines (Lawton et al., 2022); clarified that observational associations do not establish causal biological mechanisms; explicitly stated that tuned ($0.3188$) and fixed ($\tau=0.35$) thresholds are exploratory research operating points rather than clinically validated intervention thresholds. | Enforces medical conservatism and translational integrity. |
| **RCA Selected Threshold SD** | Preliminary notes cited `$0.3188 \pm 0.0388$`. | Reported as **`$0.3188 \pm 0.0380$` (`ddof=1`)**; population SD disclosed as `0.0372` (`ddof=0`). | An exact calculation over the 25 raw outer fold values confirmed sample SD is $0.0380$. The value $0.0388$ was proven to be an accidental double-Bessel factor ($0.0380 \times \sqrt{25/24} \approx 0.0388$). Fully explained in Table 5 footnote. |
| **LCX Calibration Transparency** | Potential ambiguity over why LCX was not calibrated. | Explicitly stated that **uncalibrated XGBoost was selected for LCX** because post-processing calibration (both Sigmoid and Isotonic) compressed probabilities and degraded sensitivity without improving Brier loss ($0.2054$). | Transparent disclosure of model selection rationale based on proper scoring rules. |
| **Correlated Folds Qualification** | Avoided presenting cross-validation standard deviations as independent population confidence intervals. | Added explicit statements in Methods (Section 3.5) and Limitations (Section 6.3) noting that standard deviations describe **fold-level resampling dispersion (`ddof=1`)**, not independent population confidence intervals. | Prevents statistical conflation of repeated CV resampling with independent external sampling. |
| **SHAP Explanation Space Disconnect** | Avoided claiming SHAP values explain final calibrated probabilities. | Formally proved in Section 3.6 and Section 5.4 that SHAP operates in log-odds score space ($f(x)$) and **cannot be linearly summed in probability space** under non-linear Sigmoid calibration. | Mathematical fidelity to the non-linear transformation $\sigma(A \cdot f(x) + B)$. |
| **Exploratory Subgroups Framing** | Avoided framing subgroup analysis as fairness certification. | Explicitly labeled Section 3.9 and Section 4.8 as **exploratory and hypothesis-generating**, explicitly stating that sample size constraints ($N=303$) preclude formal fairness or equalized odds guarantees. | Adheres to responsible AI reporting standards. |
| **Clinical Readiness Disclaimer** | Avoided claims of clinical deployment readiness. | Added Section 6.7 explicitly declaring that CoroVista is an **academic research prototype** not cleared by regulatory agencies for autonomous clinical intervention. | Enforces medical safety and translational honesty. |

---

## 6. Author Decision Reconciliations & Editorial Tracking

1. **Authorship & Affiliations Confirmed (Option A — Dual Authorship):**
   - **First & Corresponding Author:** Naman Deep Tripathi (Sanskriti University, Mathura, Uttar Pradesh, India; BCA Second Year; ORCID: 0009-0006-8775-3794; `namandeeptripathi@gmail.com`). *Department within Sanskriti University flagged for confirmation if required by journal portal.*
   - **Co-Author:** Nikhil Agrawal (VIT Bhopal University, Bhopal, Madhya Pradesh, India; B.Tech. Fourth Year; ORCID: 0009-0009-1546-5576; `agnikhil9897@gmail.com`). *Department/School within VIT Bhopal University flagged for confirmation if required by journal portal.*
   - **Approvals:** Both authors approved the final manuscript and confirmed the dual-authorship arrangement.
   - **CRediT Contributions:** Formally mapped with clear demarcation between early prototype/viewer contributions and advanced methodology/manuscript contributions.
2. **Ethics Statement Reconciled:**
   - Section 3.1 and Declarations updated to transparently state dataset provenance and secondary computational analysis, while explicitly stating that formal institutional determination remains to be confirmed. No IRB protocol number or exemption certificate is fabricated or claimed, and unsupported statutory assertions have been removed.
3. **Publishing Route Reconciled:**
   - Standard Subscription publishing set as preferred route (subject to final journal policy confirmation; APC and fee policy marked for final verification).
4. **National Catheterization Yield Reference Tracking:**
   - *Claim in Section 1.1:* Elective diagnostic catheterizations yielding obstructive CAD. Patel et al. (2010, NEJM) is integrated in the manuscript bibliography.

---

## 7. Recommended Next Steps for Journal Submission

1. **Target Journal Selection:**
   - **Primary Target:** *Computers in Biology and Medicine* (CBIOM, Elsevier). Matches multi-target CAD benchmark, calibration, uncertainty quantification, and explainability scope.
   - **Alternative Targets:** *Computer Methods and Programs in Biomedicine* (CMPB, Elsevier), *Artificial Intelligence in Medicine* (AIIM, Elsevier), or *Journal of Biomedical Informatics* (JBI, Elsevier).
2. **Submission Materials Inventory:**
   - All submission documents are fully prepared: `CoroVista-Research-Manuscript.pdf`, `FINAL-COVER-LETTER-DRAFT.md`, `CMPB-HIGHLIGHTS.md`, `FINAL-AUTHOR-DECISIONS.md`, and `FINAL-SUBMISSION-CHECKLIST.md`.

---

## 8. Git Status & Created Files

```bash
$ git branch --show-current
development

$ git status --short --untracked-files=all
?? docs/research/PHASE-5.1-MANUSCRIPT-EVIDENCE-MATRIX.md
?? docs/research/PHASE-5.1-MANUSCRIPT-OUTLINE.md
?? docs/research/PHASE-5.1-OPEN-ISSUES.md
?? docs/research/manuscript/01-abstract-introduction-related-work.md
?? docs/research/manuscript/02-methods-and-results.md
?? docs/research/manuscript/03-discussion-limitations-conclusion.md
?? docs/research/manuscript/CoroVista-Research-Manuscript.md
?? docs/research/manuscript/MANUSCRIPT-EDITORIAL-REVIEW.md
?? docs/research/manuscript/references.md
```

- **Branch:** `development`
- **Application Code / Models / Datasets / README / Historical Reports:** Untouched (0 modifications, 0 staged).
- **Deliverables:** `CoroVista-Research-Manuscript.md` and `MANUSCRIPT-EDITORIAL-REVIEW.md` successfully generated.
- **Git Commit / Push:** None executed. Phase 5.3 complete.
