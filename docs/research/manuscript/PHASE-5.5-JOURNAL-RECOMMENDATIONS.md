# Phase 5.5: Journal Recommendations and Submission Strategy

**Project:** CoroVista — Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction  
**Document Type:** Strategic Journal Selection, Author Guidelines & Submission Analysis  
**Auditor & Reviewer:** Independent Senior Biomedical ML Researcher & Journal Submission Specialist  
**Date:** November 15, 2026  
**Repository Branch:** `development`  
**Target Manuscript:** `docs/research/manuscript/CoroVista-Research-Manuscript.md`  

---

## 1. Executive Summary & Selection Strategy

The CoroVista research manuscript presents a comprehensive, multi-target machine learning investigation for non-invasive coronary artery disease prediction, emphasizing **probability calibration, explanation stability, prediction churn, defensive uncertainty quantification, and input robustness** on the extended Z-Alizadeh Sani cohort ($N=303$).

To maximize editorial receptivity, scholarly impact, and rapid peer review, candidate journals must satisfy five strict criteria:
1. **Established Precedent with the Cohort:** A demonstrated track record of publishing machine learning research utilizing the Z-Alizadeh Sani cardiovascular benchmark.
2. **Methodological Focus on Clinical AI Reliability:** An editorial charter that values probability calibration, error analysis, and stability auditing over raw accuracy competition.
3. **Legitimate Scientific Indexing:** Full indexing in major biomedical databases, including **PubMed / MEDLINE, Scopus, and Web of Science (Science Citation Index Expanded [SCIE])**. No predatory or unindexed venues.
4. **Flexible Length / Structural Capacity:** Ability to accommodate extensive multi-target tables, reliability curves, and comprehensive cross-validation methodology (either in main text or as supplementary material).
5. **Fair Publishing Models:** Availability of non-APC subscription publishing pathways (green open access / zero-fee publishing) alongside optional gold open access.

Based on these criteria, **five peer-reviewed biomedical informatics and clinical AI journals** have been investigated and ranked.

---

## 2. Comparative Candidate Journal Matrix

| Metric / Dimension | 1. Computer Methods and Programs in Biomedicine | 2. Journal of Biomedical Informatics | 3. Artificial Intelligence in Medicine | 4. npj Digital Medicine | 5. IEEE Journal of Biomedical and Health Informatics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Publisher** | Elsevier | Elsevier | Elsevier | Springer Nature | IEEE Engineering in Medicine and Biology |
| **Official URL** | [Elsevier CMPB](https://www.sciencedirect.com/journal/computer-methods-and-programs-in-biomedicine) | [Elsevier JBI](https://www.sciencedirect.com/journal/journal-of-biomedical-informatics) | [Elsevier AIIM](https://www.sciencedirect.com/journal/artificial-intelligence-in-medicine) | [Nature npj Digit. Med.](https://www.nature.com/npjdigitalmed/) | [IEEE JBHI](https://embs.ieeexplore.ieee.org/journal/jbhi) |
| **Journal Impact Factor (approx.)** | ~4.9–5.6 (Q1) | ~4.5–5.2 (Q1) | ~6.1–7.5 (Q1) | ~12.0–15.0 (Top 1%) | ~6.8–7.7 (Q1) |
| **Primary Indexing** | PubMed, MEDLINE, Scopus, Web of Science (SCIE) | PubMed, MEDLINE, Scopus, Web of Science (SCIE) | PubMed, MEDLINE, Scopus, Web of Science (SCIE) | PubMed, MEDLINE, Scopus, Web of Science (SCIE) | PubMed, MEDLINE, Scopus, Web of Science (SCIE) |
| **Cohort Precedent** | **Supreme (Original Venue):** Alizadehsani et al. 2013, 2018; Arabasadi 2017; Abdar 2019 | Moderate (Publishes clinical ML audits and calibration studies) | High (Publishes cardiovascular AI and explainability studies) | Low on this cohort; High on uncertainty & clinical AI safety | Moderate (Publishes tabular CAD and ML frameworks) |
| **Article Type** | Original Research Paper | Original Research Paper / Methodological Study | Regular Research Paper | Article | Regular Paper |
| **Main Text Word Guidance** | ~6,000–8,500 words (flexible for extensive studies) | ~5,000–8,000 words (structured abstract $\le 250$ words) | Up to 8,000 words | 4,000–5,000 words (strict main text; rest in Ext Data) | 8 published pages in IEEE format (~6,000 words) |
| **Table & Figure Limits** | No strict limit (excess moved to Supplementary) | Typically 6–8 display items in main text | Flexible display item allocation | Up to 6–8 display items; remainder in Extended Data | Up to 8 pages free; overlength charges apply |
| **Publication Model & APC** | **Hybrid:** \$0 under subscription; optional OA \$2,980 USD | **Hybrid:** \$0 under subscription; optional OA \$3,200 USD | **Hybrid:** \$0 under subscription; optional OA \$3,300 USD | **Full Open Access Only:** \$4,590 USD APC | **Hybrid:** \$0 under subscription; optional OA \$2,495 USD |
| **Overall Suitability Rank** | **Rank 1 (Top Recommendation)** | **Rank 2 (Methodological Alternate)** | **Rank 3 (Clinical AI Alternate)** | **Rank 4 (High-Impact Stretch)** | **Rank 5 (Engineering Alternate)** |

---

## 3. In-Depth Journal Evaluations

### 3.1 Rank 1 (Primary Recommendation): *Computer Methods and Programs in Biomedicine* (CMPB)

- **Publisher:** Elsevier
- **Official Portal:** [https://www.sciencedirect.com/journal/computer-methods-and-programs-in-biomedicine](https://www.sciencedirect.com/journal/computer-methods-and-programs-in-biomedicine)
- **Aims & Scope:** CMPB covers computational methods, algorithms, software systems, and data processing applied to clinical medicine and biomedical research. It specifically welcomes reproducible research, comparative benchmarking, and clinical decision support algorithms in cardiovascular medicine.
- **Why It Is the Ideal Match:**
  1. **Historical Home of the Z-Alizadeh Sani Cohort:** The foundational paper describing the dataset (*Alizadehsani et al., 2013*), the artery-specific prediction study (*Alizadehsani et al., 2018*), the genetic-neural network study (*Arabasadi et al., 2017*), and the Nu-SVC ensemble benchmark (*Abdar et al., 2019*) were all published in CMPB.
  2. **Editorial Receptivity to Reliability Re-Evaluations:** CMPB editors and reviewers are intimately familiar with this dataset. A rigorous re-evaluation that demonstrates data leakage in prior works, implements nested probability calibration, resolves sensitivity collapse on RCA, and evaluates SHAP stability will be perceived as a direct, valuable contribution to the ongoing scientific discourse in their own journal.
  3. **Zero Financial Barrier:** Authors can publish under the traditional subscription model with **\$0 author fees**, or select Gold Open Access if grant funding is available.
- **Submission Requirements:**
  - *Article Type:* Original Research Paper.
  - *Abstract:* Structured abstract ($\le 250$ words: Background, Methods, Results, Conclusions).
  - *Keywords:* 4–6 MeSH-aligned keywords.
  - *Length Adaptation:* The manuscript can be submitted in full, with minor reorganization moving Tables 10–12 and supplementary ablation text into an online Supplementary Material file if requested by the handling editor.

---

### 3.2 Rank 2 (First Methodological Alternative): *Journal of Biomedical Informatics* (JBI)

- **Publisher:** Elsevier
- **Official Portal:** [https://www.sciencedirect.com/journal/journal-of-biomedical-informatics](https://www.sciencedirect.com/journal/journal-of-biomedical-informatics)
- **Aims & Scope:** JBI focuses on innovative methodology in biomedical informatics. It explicitly requires papers to demonstrate generalizable methodological principles rather than merely presenting a domain-specific model application.
- **Why It Fits:**
  - CoroVista's core thesis—that standard discrimination benchmarking must be supplemented with probability calibration, explainability stability auditing across resampled folds, boundary prediction churn tracking, and defensive uncertainty quantification—is fundamentally a biomedical informatics methodological framework.
  - JBI highly values proper scoring rules (Brier scores), error triage mechanisms, and rigorous reporting standards (TRIPOD+AI).
- **Considerations:** JBI reviewers will demand that the manuscript emphasize the generalizable evaluation framework over the specific single-center CAD findings. Authors would need to highlight CoroVista as an extensible reliability auditing methodology applicable to medical tabular data broadly.
- **Publishing Cost:** Hybrid (\$0 subscription pathway available).

---

### 3.3 Rank 3 (Clinical Decision Support Alternative): *Artificial Intelligence in Medicine* (AIIM)

- **Publisher:** Elsevier
- **Official Portal:** [https://www.sciencedirect.com/journal/artificial-intelligence-in-medicine](https://www.sciencedirect.com/journal/artificial-intelligence-in-medicine)
- **Aims & Scope:** AIIM publishes original theoretical and applied contributions on AI in healthcare, clinical decision support systems, medical knowledge representation, explainable AI, and medical machine learning validation.
- **Why It Fits:**
  - Strong emphasis on explainable AI (XAI) and clinical decision support safety.
  - CoroVista's TreeSHAP and LinearSHAP stability analysis across 25 outer folds and 300 pairwise fold comparisons, paired with predictive entropy for automated error flagging, directly targets AIIM's core readership.
- **Publishing Cost:** Hybrid (\$0 subscription pathway available).

---

### 3.4 Rank 4 (High-Impact Stretch): *npj Digital Medicine*

- **Publisher:** Springer Nature
- **Official Portal:** [https://www.nature.com/npjdigitalmed/](https://www.nature.com/npjdigitalmed/)
- **Aims & Scope:** High-impact Nature Partner journal focusing on digital health, clinical AI translation, predictive modeling, and biomedical data science.
- **Why It Fits:** Published foundational perspective pieces on clinical uncertainty (Kompa et al., 2021) and AI reporting governance.
- **Barriers & Trade-offs:**
  1. *Strict Word Limit:* Requires main text between 4,000 and 5,000 words. Submitting our 17,268-word comprehensive manuscript would require aggressive restructuring, shifting 60% of the methodological text and secondary tables into Extended Data.
  2. *APC Requirement:* As a fully open-access journal, it requires an article processing charge of approximately **\$4,590 USD** with no subscription fee waiver.
  3. *Validation Expectation:* Editors frequently favor papers that include multi-center external validation or prospective clinical trials.

---

### 3.5 Rank 5 (Biomedical Engineering Alternative): *IEEE Journal of Biomedical and Health Informatics* (J-BHI)

- **Publisher:** IEEE Engineering in Medicine and Biology Society
- **Official Portal:** [https://embs.ieeexplore.ieee.org/journal/jbhi](https://embs.ieeexplore.ieee.org/journal/jbhi)
- **Aims & Scope:** Focuses on computational informatics, signal processing, and machine learning methods across health systems.
- **Considerations:** Requires formatting in IEEE two-column style. Overlength page charges apply beyond 8 printed pages.

---

## 4. Strategic Submission Plan & Step-by-Step Workflow

### Recommended Venue: **Computer Methods and Programs in Biomedicine (CMPB)**

1. **Step 1: Complete Author-Dependent Disclosures**
   - Confirm final author order, affiliations, and corresponding email address (see `PHASE-5.5-AUTHOR-CONFIRMATION-REQUIRED.md`).
   - Query Shaheed Rajaei institutional archives for any historical registry approval identifier; if unavailable, retain the current secondary analysis exemption disclosure.
2. **Step 2: Format Manuscript to Elsevier Guide for Authors**
   - Retain full text in single-column, double-spaced format with line numbers.
   - Separate figures into standalone high-resolution TIFF or PNG files ($\ge 300$ DPI).
   - Ensure tables are placed either in-text or gathered at the end, as preferred by Editorial Manager.
3. **Step 3: Prepare Submission Package**
   - Draft Cover Letter addressed to the Editor-in-Chief highlighting the paper's role in advancing the Z-Alizadeh Sani benchmark through probability calibration and stability auditing.
   - Prepare a 3–5 bullet Highlights file ($\le 85$ characters per bullet).
   - Prepare the graphical abstract using Figure 1 / Figure 3 summary assets.
4. **Step 4: Select Publishing Route**
   - Select the **Subscription Model (\$0 APC)** upon submission unless institutional open-access agreements apply.
