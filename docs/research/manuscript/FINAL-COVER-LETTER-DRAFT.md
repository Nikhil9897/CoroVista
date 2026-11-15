# Cover Letter: CoroVista Research Manuscript

**Date:** [Date of Submission, e.g., November 16, 2026]  

**To:**  
The Editor-in-Chief  
*[Journal Name, e.g., Computer Methods and Programs in Biomedicine / Artificial Intelligence in Medicine]*  
Elsevier / Nature Portfolio  

**Subject:** Submission of Original Research Manuscript titled **"Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness"**

Dear Editor-in-Chief and Editorial Board Members,

We are pleased to submit our original research manuscript entitled **"Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness"** for consideration for publication as a **Full Length Research Article** in *[Target Journal Name]*.

### Context & Scientific Motivation
Machine learning algorithms for non-invasive coronary artery disease (CAD) risk assessment are frequently benchmarked solely on composite discrimination metrics (such as ROC-AUC) on single train-test partitions. However, high discrimination reported in literature often masks critical vulnerabilities: severe probability miscalibration, volatile feature attribution rankings across data resampling, and localized prediction instability near classification cutoffs. 

In this investigation, we present **CoroVista**, an end-to-end multi-target framework evaluating overall CAD (`Cath`) and vessel-specific stenosis across the three major epicardial coronary territories: Left Anterior Descending (`LAD`), Left Circumflex (`LCX`), and Right Coronary Artery (`RCA`).

### Key Methodological Contributions & Findings
1. **Target-Specific Calibration Hierarchy:** We show that while Platt Sigmoid scaling regularizes probability estimates for `Cath` (ECE 0.1004) and `LAD` (ECE 0.1326), post-hoc calibration on `LCX` compresses probabilities into an uninformative narrow band near the base rate. We demonstrate that empirical validation against proper scoring rules (Brier score) must guide calibration selection rather than applying calibration dogmatically.
2. **Resolution of Calibrated Sensitivity Collapse:** Applying standard midpoint thresholds ($\tau = 0.50$) to calibrated minority-class models (`RCA`, prevalence 37.62%) resulted in severe clinical sensitivity collapse (Recall $31.24\% \pm 8.56\%$). We demonstrate that nested inner-fold threshold tuning restores clinical sensitivity to $79.46\% \pm 10.92\%$ ($F_1 = 0.6037 \pm 0.0516$) without test-partition data leakage, and fixed production thresholding ($\tau = 0.35$) yields robust sensitivity ($74.21\% \pm 10.64\%$ across 25 outer folds; $74.21\% \pm 2.53\%$ across 5 repeats).
3. **Multi-Fold Attribution Stability:** Evaluating 300 pairwise cross-validation fold comparisons, TreeSHAP feature importance rankings for tree ensembles demonstrated high stability (Spearman $\rho = 0.9319$ for Cath; $0.9217$ for LAD), whereas regularized linear models for RCA exhibited ranking volatility ($\rho = 0.7737$). Exact mathematical additivity ($\sum \phi_i + \phi_0 = f(x)$) was verified in 100% of folds ($25/25$).
4. **Anatomy of Prediction Invariance:** We quantify prediction churn across model retraining. While confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance across repeated training runs, predictions in the immediate threshold margin ($|p - \tau| < 0.05$) exhibited 100% label flipping, exposing a critical epistemic boundary in clinical AI.
5. **Physiological Territory Divergence:** Inside-cross-validation feature ablation revealed branch-specific mechanisms: LAD was driven predominantly by echocardiography (`Region RWMA`, `EF-TTE`), whereas LCX relied primarily on serum biochemistry panels (`CR`, `TG`, `PLT`).

### Mandatory Editorial & Ethical Declarations
- **Originality:** This manuscript represents original work that has not been published previously, is not under consideration for publication elsewhere, and will not be submitted elsewhere while under review at *[Journal Name]*.
- **Data Governance & Research Ethics:** This investigation is an independent secondary computational re-analysis conducted exclusively on the publicly accessible, de-identified Z-Alizadeh Sani cardiology dataset obtained from the UCI Machine Learning Repository (DOI: [10.24432/C5Q31T](https://doi.org/10.24432/C5Q31T)) and Mendeley Data (DOI: [10.17632/9k56pwtvz9.1](https://doi.org/10.17632/9k56pwtvz9.1)) under Creative Commons Attribution 4.0 International (**CC BY 4.0**). The authors were not involved in primary patient recruitment, clinical catheterization, or biological specimen collection, and possess no re-identification keys. In accordance with international biomedical data governance standards (e.g., US 45 CFR § 46.104(d)(4), UK Health Research Authority, and ICMR Guidelines), secondary research on open, fully de-identified public data does not involve direct human subjects intervention.
- **Reporting Standards:** The manuscript adheres to the **TRIPOD+AI** reporting guidelines for clinical prediction models. We explicitly qualify that our findings represent internal cross-validation and that prospective external clinical validation is required prior to diagnostic deployment.
- **Competing Interests:** The authors declare that they have no competing financial interests, personal relationships, or corporate affiliations that could have influenced the work.
- **Funding:** This research received no external grant funding from public, commercial, or non-profit entities.
- **Open Science & Reproducibility:** All data processing pipelines, model configurations, cross-validation splits, and reproduction evaluation scripts are maintained openly in the research repository.

### Corresponding Author Contact Information
**Name:** Naman Deep Tripathi  
**Role:** Lead Machine Learning Researcher & Systems Architect  
**Affiliation:** [Department / Institution / Independent Researcher designation, City, Country]  
**Email:** [namandeeptripathi@gmail.com / institutional email]  
**ORCID:** [Author ORCID identifier, e.g., https://orcid.org/XXXX-XXXX-XXXX-XXXX]  

We believe this paper provides essential methodological guidance for researchers working on cardiovascular machine learning, probability calibration, explainable AI, and model reliability. Thank you very much for your time and consideration of our manuscript.

Sincerely,

**Naman Deep Tripathi**  
*(On behalf of the authors)*
