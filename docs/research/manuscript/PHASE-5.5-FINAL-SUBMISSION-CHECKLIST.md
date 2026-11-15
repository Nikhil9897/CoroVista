# Phase 5.5: Final Journal Submission Checklist

**Project:** CoroVista — Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction  
**Document Type:** Actionable Pre-Submission Verification & Compliance Checklist  
**Target Venue:** *Computer Methods and Programs in Biomedicine* (or alternate biomedical informatics journal)  
**Date:** November 15, 2026  
**Repository Branch:** `development`  

---

## Instructions for Authors

This checklist details every operational, editorial, ethical, and technical task that the author team must complete prior to uploading the CoroVista manuscript to the journal submission portal (e.g., Elsevier Editorial Manager).

---

## 1. Administrative, Author & Contact Metadata

- [ ] **Author Order & Roles:** Confirm final co-author sequence:
  1. *Naman Deep Tripathi* (First & Corresponding Author / Lead ML Architect)
  2. *Nikhil Agrawal* (Co-Author / Clinical Domain & Anatomical Asset Lead)
- [ ] **Institutional Affiliations:** Replace placeholder institutional tags with formal departmental titles, academic institutions, city, state/province, and country for each author.
- [ ] **ORCID Identifiers:** Retrieve and link active ORCID IDs for all co-authors (e.g., `0000-xxxx-xxxx-xxxx`).
- [ ] **Corresponding Author Information:** Designate the official corresponding author and record their institutional email address, telephone number, and physical mailing address.
- [ ] **Cover Letter Preparation:** Draft a formal cover letter addressed to the Editor-in-Chief of the selected journal:
  - Summarize the paper's core contributions (multi-target vessel prediction, probability calibration, SHAP stability, defensive uncertainty).
  - Emphasize adherence to TRIPOD+AI reporting guidelines.
  - State that the manuscript is original, has not been published elsewhere, and is not under consideration at another journal.
  - Declare no financial or personal conflicts of interest.
  - Suggest 3–5 qualified, non-conflicted peer reviewers (independent experts in cardiovascular machine learning, explainable AI, or biomedical calibration).

---

## 2. Research Ethics & Data Governance Declarations

- [ ] **Institutional Ethics Protocol Query (Shaheed Rajaei):**
  - Check whether an archival Institutional Review Board / Ethics Committee approval protocol number exists for the historical Z-Alizadeh Sani cohort collected at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran).
  - *If a protocol number is found:* Insert the official protocol identifier into Section 3.1 and Declarations.
  - *If no protocol number is available:* Retain the current transparent secondary analysis disclosure:
    > *"Because this study represents an independent secondary computational investigation performed exclusively on previously published, fully de-identified, publicly accessible research data involving no prospective clinical intervention, no biological specimen collection, and no patient re-identification potential, formal institutional human subjects ethical review and individual patient informed consent are considered not applicable under international biomedical research data governance guidelines."*
- [ ] **Consent for Publication:** Confirm the "Not applicable" statement (no personally identifiable individual images or biometric records included).
- [ ] **Data Availability Statement:** Verify the accuracy of public repository DOI links:
  - UCI Machine Learning Repository: [DOI 10.24432/C5Q31T](https://doi.org/10.24432/C5Q31T)
  - Mendeley Data Repository: [DOI 10.17632/9k56pwtvz9.1](https://doi.org/10.17632/9k56pwtvz9.1)
- [ ] **Code Availability Statement:** Provide the permanent GitHub repository URL or Zenodo archive DOI for CoroVista evaluation scripts.
- [ ] **Funding & Competing Interests:** Formally affirm that no external commercial or public grant funding influenced the study, and that authors have no competing financial interests.

---

## 3. Scientific Methodology & Reporting Compliance

- [ ] **TRIPOD+AI Statement Completeness:**
  - Verify that all 20 applicable items of the TRIPOD+AI checklist (Collins et al., 2024, BMJ) are fully addressed across Title, Abstract, Methods, Results, Discussion, and Declarations.
  - Retain the itemized checklist in `docs/research/manuscript/PHASE-5.4-SCIENTIFIC-AUDIT.md` for potential submission as supplementary material.
- [ ] **Protocol Separation Integrity:**
  - Verify that nested inner-fold threshold tuning ($0.3188 \pm 0.0380$) is described as an internal out-of-fold optimization procedure to prevent leakage, rather than an independently clinically validated cutoff.
  - Verify that the fixed production cutoff ($\tau = 0.35$) is explicitly described as an experimental operating point.
- [ ] **Dispersion & Variance Notation:**
  - Confirm that all cross-validation performance metrics report sample standard deviation (`ddof=1`) as the primary dispersion statistic, with population standard deviation (`ddof=0`) noted where relevant to reconcile stored JSON artifacts.
- [ ] **Claim Boundaries & Tone:**
  - Re-verify that the text strictly avoids causal assertions, claims of clinical readiness, claims of regulatory approval (FDA/CE), claims of autonomous diagnostic substitution, or algorithmic fairness guarantees.

---

## 4. Visual Display Items (Figures & Tables)

- [ ] **Figure Asset Preparation:** Export the 6 primary manuscript figures as standalone high-resolution image files:
  - Figure 1: `roc_curves.png` and `pr_curves.png` (from `data/reports/reproduction_audit/plots/`)
  - Figure 2: `calibration_curves.png` (from `data/reports/reproduction_audit/plots/`)
  - Figure 3: `cross_target_shap_stability.png` (from `data/reports/phase4/summary/figures/`)
  - Figure 4: `cross_target_prediction_stability.png` (from `data/reports/phase4/summary/figures/`)
  - Figure 5: `uncertainty_distributions.png` (from `data/reports/phase4/uncertainty/cath/figures/`)
  - Figure 6: `feature_ablation_comparison.png` (from `data/reports/phase4/robustness/cath/figures/`)
  - Verify that all exported figure files satisfy $\ge 300$ DPI resolution and standard format requirements (TIFF, PNG, or EPS).
- [ ] **Table Placement & Formatting:**
  - Confirm that Tables 1 through 12 contain complete units, sample sizes ($N=303$), decimal precision, and explanatory table footnotes.
  - Format tables in standard journal style (three horizontal rules: top rule, column header rule, and bottom rule; no vertical grid lines).

---

## 5. Journal Submission Portal Upload Package

Prepare the following individual upload components:
1. [ ] **Main Manuscript Document:** Anonymized or unblinded (per journal single/double-blind policy) Word (`.docx`) or LaTeX/PDF file containing Title, Abstract, Keywords, Sections 1–8, Declarations, and References.
2. [ ] **Title Page (if separate):** Complete author names, credentials, institutional affiliations, corresponding author contact, acknowledgments, and word count.
3. [ ] **Highlights File:** 3 to 5 bullet points ($\le 85$ characters each, including spaces) summarizing key findings:
   - Multi-target ML models predict composite CAD and artery-specific stenosis.
   - Sigmoid calibration resolves probability distortion but induces RCA sensitivity collapse.
   - Nested threshold tuning restores clinical sensitivity to 79.5% without data leakage.
   - TreeSHAP explanations exhibit high global stability ($\rho > 0.90$) across resampled folds.
   - Predictive entropy discriminates empirical misclassifications without ground-truth labels.
4. [ ] **Graphical Abstract:** Visual summary panel highlighting multi-vessel prediction, calibration curves, and SHAP stability.
5. [ ] **High-Resolution Figures:** Standalone image files labeled `Figure1.tiff` through `Figure6.tiff`.
6. [ ] **Supplementary Material File (if needed):** Supplementary methods, extended ablation tables (Tables 10–12), and the TRIPOD+AI itemized audit checklist.
