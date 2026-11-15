# CoroVista: Final Practical Journal Submission Checklist

**Document:** Operational Journal Submission Checklist  
**Target Venue:** *Computer Methods and Programs in Biomedicine* (CMPB, Elsevier) [Primary] / *Artificial Intelligence in Medicine* (AIIM, Elsevier) [Alternative]  
**Manuscript Title:** *Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness*  
**Canonical PDF Artifact:** `CoroVista-Research-Manuscript.pdf` (29 pages, SHA-256: `38cb02c18ceb38f26df78d068d1054d7e591ca96282bbcfe4b51752641d1c014`)

---

## Phase 1: Pre-Submission Preparation (Author Sign-Off)

Before logging into the Elsevier Editorial Manager portal, verify the following author-confirmed items:

- [ ] **1. Authorship Finalized (`FINAL-AUTHOR-DECISIONS.md`):**
  - Confirmed whether submitting as **Dual Authors** (`Naman Deep Tripathi`, `Nikhil Agrawal`) or **Sole Author** (`Naman Deep Tripathi` with Nikhil Agrawal acknowledged).
  - Confirmed author order and corresponding author designation.
- [ ] **2. Author Metadata Confirmed:**
  - Verified institutional department, university, city, country (or Independent Researcher status).
  - Active corresponding email address confirmed.
  - Active ORCID identifier confirmed ([orcid.org](https://orcid.org)).
- [ ] **3. Cover Letter Customized (`FINAL-COVER-LETTER-DRAFT.md`):**
  - Target journal name, editor name, and date updated.
  - Corresponding author affiliation and contact info inserted.
- [ ] **4. Publishing Route Selected:**
  - Standard **Subscription Route (\$0 APC — Free to author)** selected, OR Gold Open Access confirmed.

---

## Phase 2: Submission Portal File Inventory

Ensure the following files are ready for upload on the submission portal:

| Item # | Portal Category | File Name / Path | Format / Size | Status |
|:---:|---|---|:---:|:---:|
| **1** | **Manuscript (with embedded tables & figures)** | `CoroVista-Research-Manuscript.pdf` | PDF (2.1 MB, 29 pp) | **READY** |
| **2** | **Manuscript Editable Source** | `docs/research/manuscript/CoroVista-Research-Manuscript.md` | Markdown / Text | **READY** |
| **3** | **Cover Letter** | `FINAL-COVER-LETTER-DRAFT.md` | PDF / Word / Text | **READY** |
| **4** | **Figure 1 (High-Res)** | `data/reports/reproduction_audit/plots/roc_curves.png` | PNG (225 KB) | **READY** |
| **5** | **Figure 2 (High-Res)** | `data/reports/reproduction_audit/plots/calibration_curves.png` | PNG (727 KB) | **READY** |
| **6** | **Figure 3 (High-Res)** | `data/reports/phase4/summary/figures/cross_target_shap_stability.png` | PNG (140 KB) | **READY** |
| **7** | **Figure 4 (High-Res)** | `data/reports/phase4/summary/figures/cross_target_prediction_stability.png` | PNG (156 KB) | **READY** |
| **8** | **Figure 5 (High-Res)** | `data/reports/phase4/uncertainty/cath/figures/uncertainty_distributions.png` | PNG (189 KB) | **READY** |
| **9** | **Figure 6 (High-Res)** | `data/reports/phase4/robustness/cath/figures/feature_ablation_comparison.png` | PNG (115 KB) | **READY** |
| **10** | **Supplementary Data / Code** | Project GitHub / Zenodo Archive Repository | URL / ZIP Archive | **READY** |

---

## Phase 3: Editorial Manager Form Fields Quick-Reference

When completing the web-form fields in Elsevier Editorial Manager:

### 1. Article Type:
- Select: **Full Length Article** (or **Original Research Paper**).

### 2. Article Title:
```text
Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness
```

### 3. Running Title / Short Title:
```text
CoroVista: Reliable & Explainable CAD Prediction
```

### 4. Abstract:
Copy and paste the structured abstract from Page 1 of the manuscript (Background, Methods, Results, Conclusions). Ensure the RCA threshold statistics read:
> *"Recall 74.21% ± 10.64% across 25 outer folds [74.21% ± 2.53% across 5 repeats], Specificity 57.48% ± 7.10% [57.46% ± 1.10% across 5 repeats]"*

### 5. Keywords (Up to 8 keywords):
```text
Coronary Artery Disease; Multi-Vessel Stenosis; Probability Calibration; SHAP Stability; Prediction Stability; Uncertainty Quantification; Diagnostic Angiography; Machine Learning
```

### 6. CRediT Author Statement:
```text
Naman Deep Tripathi: Conceptualization, methodology formulation, machine learning architecture, cross-validation protocols, calibration modeling, explainability stability algorithms, uncertainty quantification framework, software implementation, manuscript drafting, and editorial review.
Nikhil Agrawal: Cardiovascular domain mapping, anatomical multi-target localization, 3D anatomical asset integration (Mitsuhashi et al., 2009), clinical workflow visualization, data audit, and critical manuscript review.
```
*(Adjust if sole authorship is selected).*

### 7. Declaration of Competing Interests:
```text
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.
```

### 8. Funding Statement:
```text
This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.
```

### 9. Data Availability Statement:
```text
The extended Z-Alizadeh Sani cardiology dataset utilized in this investigation is openly available in public data repositories: UCI Machine Learning Repository (DOI: 10.24432/C5Q31T) and Mendeley Data Repository (DOI: 10.17632/9k56pwtvz9.1). All experimental reproduction scripts and pipeline code are hosted in the project research repository.
```

### 10. Ethics Statement:
```text
The empirical data utilized in this study originate from the open-access Z-Alizadeh Sani repository, collected and anonymized at Shaheed Rajaei Cardiovascular, Medical and Research Center in Tehran, Iran (Alizadehsani et al., 2013; Alizadehsani, 2017, 2018). The foundational publications do not disclose a specific institutional review board (IRB) or ethics committee protocol identifier, operating under standard hospital clinical diagnostic data governance. Because the present investigation represents an independent secondary computational study performed exclusively on previously published, fully de-identified, publicly accessible research data involving no prospective clinical intervention, no biological specimen collection, and no patient re-identification potential, formal institutional human subjects ethical review and individual patient informed consent are not applicable for this secondary analysis under international research ethics standards.
```

---

## Phase 4: Suggested Peer Reviewers

Journals frequently request 3–4 suggested reviewers. Recommended reviewer profiles with expertise in this exact domain:

1. **Cardiovascular Machine Learning & Clinical Decision Support:**
   - *Expertise:* Machine learning for coronary artery disease diagnosis, invasive angiography risk stratification.
   - *Example Domain:* Authors publishing on diagnostic CAD models and multi-vessel localization in *Computer Methods and Programs in Biomedicine*, *Circulation: Cardiovascular Quality and Outcomes*, or *JACC: Cardiovascular Imaging*.
2. **Probability Calibration & Reliability in Healthcare AI:**
   - *Expertise:* Evaluation of clinical risk prediction models, Brier scores, Expected Calibration Error, Platt scaling, and TRIPOD+AI compliance.
   - *Example Domain:* Researchers actively working on clinical probability calibration and model reliability.
3. **Explainable AI (XAI) & Attribution Stability:**
   - *Expertise:* SHAP value stability under resampling, TreeSHAP, model interpretability, and post-hoc attribution consistency in high-stakes biomedical systems.

---

## Phase 5: Submission Verification & PDF Approval

- [ ] System-generated PDF proof built by the journal portal has been downloaded and inspected.
- [ ] Figure resolution verified: ROC curves, reliability diagrams, SHAP heatmaps, and ablation bar charts render sharply.
- [ ] Table 2 (landscape) and all portrait tables render cleanly without text clipping.
- [ ] Title page, author affiliations, abstract, and references match the portal metadata exactly.
- [ ] Click **"Approve Submission"** to transmit the manuscript for editorial screening.
