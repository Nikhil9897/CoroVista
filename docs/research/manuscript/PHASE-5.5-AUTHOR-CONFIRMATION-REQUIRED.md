# Phase 5.5: Items Requiring Author Confirmation Prior to Submission

**Project:** CoroVista — Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction  
**Document Type:** Formal Author Confirmation & Missing Metadata Inventory  
**Auditor & Reviewer:** Independent Senior Biomedical ML Researcher & Journal Submission Specialist  
**Date:** November 15, 2026  
**Repository Branch:** `development`  

---

## Notice to Author Team

This document details all scientific, administrative, ethical, and institutional metadata that **cannot be resolved from repository code, datasets, or historical JSON outputs alone**, and therefore strictly require direct human confirmation from the author team (Naman Deep Tripathi and Nikhil Agrawal) prior to journal portal submission.

In strict adherence to research integrity standards, **no information in this document has been guessed, assumed, or manufactured**.

---

## 1. Itemized Author Confirmation Registry

### Item 1: Institutional Review Board (IRB) / Ethics Committee Protocol Number
- **Category:** Ethical Governance & Data Provenance
- **Current Status in Manuscript:** The manuscript explicitly declares that the cohort was collected historically at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran) and that the present secondary analysis is conducted on de-identified, publicly accessible research data.
- **Action Required from Authors:**
  1. Determine whether an official historical Institutional Review Board / Ethics Committee approval protocol number was ever registered at Shaheed Rajaei Cardiovascular Center or Iran University of Medical Sciences for the 2011–2013 data collection (e.g., by contacting Dr. Roohallah Alizadehsani or Dr. Zahra Alizadeh Sani).
  2. *Scenario A (Protocol Found):* Insert the exact protocol identifier into Section 3.1 and Declarations:  
     `"The dataset collection protocol was approved by the Institutional Ethics Committee of Shaheed Rajaei Cardiovascular, Medical and Research Center (Protocol ID: [INSERT PROTOCOL NUMBER])."`
  3. *Scenario B (No Protocol Found):* Retain the current verified disclosure:  
     `"Because this study represents an independent secondary computational investigation performed exclusively on previously published, fully de-identified, publicly accessible research data involving no prospective clinical intervention, no biological specimen collection, and no patient re-identification potential, formal institutional human subjects ethical review and individual patient informed consent are considered not applicable under international biomedical research data governance guidelines."`

---

### Item 2: Author Academic Affiliations & Institutional Details
- **Category:** Administrative & Authorship
- **Current Status in Manuscript:** Author names (*Naman Deep Tripathi* and *Nikhil Agrawal*) are listed without institutional department addresses.
- **Action Required from Authors:**
  - Provide formal department, division, school, university or hospital name, city, state/province, postal code, and country for each author.
  - Example Format:
    1. *Naman Deep Tripathi, B.Tech / M.Tech / Ph.D.* — Department of Computer Science & Engineering, [Institution Name], [City], [Country].
    2. *Nikhil Agrawal, M.B.B.S. / M.D. / M.S.* — Department of Cardiovascular Sciences / [Institution Name], [City], [Country].

---

### Item 3: Corresponding Author Designation & Contact Information
- **Category:** Administrative & Editorial Contact
- **Current Status in Manuscript:** Lead author Naman Deep Tripathi is listed as lead architect.
- **Action Required from Authors:**
  - Confirm whether Naman Deep Tripathi will serve as the sole corresponding author.
  - Provide corresponding institutional email address (e.g., `author@institution.edu`), telephone number with country code, and official physical mailing address for journal proofs.

---

### Item 4: ORCID Identifiers
- **Category:** Digital Identity & Indexing
- **Current Status in Manuscript:** Omitted from text.
- **Action Required from Authors:**
  - Supply 16-digit Open Researcher and Contributor ID (ORCID) for all co-authors:
    - Naman Deep Tripathi: `https://orcid.org/0000-xxxx-xxxx-xxxx`
    - Nikhil Agrawal: `https://orcid.org/0000-xxxx-xxxx-xxxx`

---

### Item 5: Funding Affirmation
- **Category:** Declarations & Financial Transparency
- **Current Status in Manuscript:** Declares: *"This research received no specific grant or external financial support from any funding agency in the public, commercial, or not-for-profit sectors."*
- **Action Required from Authors:**
  - Confirm whether any university internal fellowship, departmental lab allowance, or compute credits supported this project. If so, insert the grant/award number; if none, confirm the existing zero-funding declaration.

---

### Item 6: Conflict of Interest Formal Affirmation
- **Category:** Declarations & Commercial Relationships
- **Current Status in Manuscript:** Declares: *"The authors declare that they have no competing financial interests, personal relationships, or corporate affiliations that could have influenced the work reported in this paper."*
- **Action Required from Authors:**
  - Confirm that neither author has personal, consulting, advisory, or patent interests with commercial cardiovascular software vendors or pharmaceutical entities.

---

### Item 7: Authors' Contributions Breakdown (CRediT Taxonomy)
- **Category:** Authorship Governance
- **Current Status in Manuscript:** Outlines broad responsibilities.
- **Action Required from Authors:**
  - Review and confirm the formal Contributor Roles Taxonomy (CRediT) distribution:
    - **Naman Deep Tripathi:** Conceptualization, Methodology, Software, Formal Analysis, Investigation, Data Curation, Writing – Original Draft, Writing – Review & Editing, Visualization, Project Administration.
    - **Nikhil Agrawal:** Conceptualization (cardiovascular domain), Validation, Investigation (anatomical 3D asset mapping), Resources, Writing – Review & Editing.

---

### Item 8: Code Repository Public Accessibility & Licensing
- **Category:** Reproducibility & Open Science
- **Current Status in Manuscript:** States: *"All open-source software, preprocessing pipelines, model configurations, and experimental evaluation scripts developed for CoroVista are hosted in the project research repository."*
- **Action Required from Authors:**
  - Verify that the target GitHub repository (or Zenodo archive) will be public at the time of manuscript submission or review, and confirm the open-source license (e.g., MIT, Apache 2.0, or GPLv3).

---

## 2. Summary of Author Action Steps

| # | Action Item | Target Location | Responsible Person | Completed? |
| :-: | :--- | :--- | :---: | :---: |
| 1 | IRB protocol query (Shaheed Rajaei) | Section 3.1 & Declarations | Author Team | [ ] |
| 2 | Supply full institutional affiliations | Title Page / Author List | N. D. Tripathi / N. Agrawal | [ ] |
| 3 | Supply corresponding author email & address | Title Page | N. D. Tripathi | [ ] |
| 4 | Provide ORCID identifiers | Title Page | Both Authors | [ ] |
| 5 | Confirm zero external funding | Declarations | Author Team | [ ] |
| 6 | Confirm zero conflicts of interest | Declarations | Author Team | [ ] |
| 7 | Confirm CRediT contribution mapping | Declarations | Both Authors | [ ] |
| 8 | Ensure public code repository URL | Declarations | N. D. Tripathi | [ ] |
