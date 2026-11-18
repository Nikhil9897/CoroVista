# CoroVista: Consolidated Final Author Decisions

**Document:** Author Confirmation & Submission Sign-Off Document  
**Date:** November 16, 2026  
**Scope:** Specific, actionable decisions and metadata required from the author prior to uploading the CoroVista manuscript to a journal submission portal.

---

## 1. Authorship Reconciliation Decision

The git repository history documents early prototype contributions by **Nikhil Agrawal** (initial dataset upload, exploratory scripts, frontend UI, 3D anatomical viewer integration) and advanced research methodology, validation rigour, stability/robustness experiments, and manuscript authorship by **Naman Deep Tripathi**. 

Under international biomedical authorship standards (**ICMJE guidelines**), co-authors must have contributed substantially to the research conception/execution, critically revised the manuscript for important intellectual content, and approved the final submission.

### Select One Option:

- [ ] **Option A: Dual Authorship (Recommended if CRediT statement is endorsed by both)**
  - **Authors:** Naman Deep Tripathi (First & Corresponding Author), Nikhil Agrawal (Co-Author).
  - **CRediT Statement:**
    - *Naman Deep Tripathi:* Conceptualization, methodology formulation, machine learning architecture, cross-validation protocols, calibration modeling, explainability stability algorithms, uncertainty quantification framework, software implementation, manuscript drafting, and editorial review.
    - *Nikhil Agrawal:* Cardiovascular domain mapping, anatomical multi-target localization, 3D anatomical asset integration (Mitsuhashi et al., 2009), clinical workflow visualization, data audit, and critical manuscript review.

- [ ] **Option B: Sole Authorship (Recommended if this was an independent solo research project)**
  - **Author:** Naman Deep Tripathi (Sole Author).
  - **Nikhil Agrawal Recognition:** Move Nikhil Agrawal to the `Acknowledgements` section for his technical integration of the 3D heart visualization tool and early data exploration.

---

## 2. Author Institutional Affiliation & Contact Metadata

Academic journals mandate verified institutional affiliations, corresponding author email, and ORCID identifiers on the title page and metadata forms.

Please provide or confirm the exact text for:

1. **First / Corresponding Author (Naman Deep Tripathi):**
   - **Full Name:** Naman Deep Tripathi
   - **Affiliation Option 1 (Student / Academic):** Department of [e.g., Computer Science & Engineering], [University / College Name], [City], [State], India.
   - **Affiliation Option 2 (Independent):** Independent Researcher, [City], India.
   - **Corresponding Email:** `[namandeeptripathi@gmail.com]` or `[student@university.edu]`
   - **ORCID ID:** `[e.g., 0000-000X-XXXX-XXXX]` (Free to create at [orcid.org](https://orcid.org))

2. **Co-Author (Nikhil Agrawal) — *Only required if Option A is selected*:**
   - **Full Name:** Nikhil Agrawal
   - **Affiliation:** Department of [e.g., Computer Science & Engineering], [University Name], [City], India (or Independent Researcher).
   - **Email:** `[agnikhil9897@gmail.com]`
   - **ORCID ID:** `[Optional or 0000-000X-XXXX-XXXX]`

---

## 3. Ethics Statement Sign-Off

The manuscript's ethics declarations in Section 3.1 and the Declarations section have been updated to replace internal audit placeholders with the following transparent, defensible language:

> *"The empirical data utilized in this study originate from the open-access Z-Alizadeh Sani repository, collected and anonymized at Shaheed Rajaei Cardiovascular, Medical and Research Center in Tehran, Iran (Alizadehsani et al., 2013; Alizadehsani, 2017, 2018). The foundational publications do not disclose a specific institutional review board (IRB) or ethics committee protocol identifier, operating under standard hospital clinical diagnostic data governance. Because the present investigation represents an independent secondary computational study performed exclusively on previously published, fully de-identified, publicly accessible research data involving no prospective clinical intervention, no biological specimen collection, and no patient re-identification potential, formal institutional human subjects ethical review and individual patient informed consent are not applicable for this secondary analysis under international research ethics standards."*

- [ ] **Confirmed:** I approve this transparent secondary research ethics disclosure.

---

## 4. Acknowledgements Section Sign-Off

The following formal acknowledgement has been incorporated into the manuscript:

> *"The authors express their sincere gratitude to Dr. Zahra Alizadeh Sani, Dr. Roohallah Alizadehsani, and their clinical colleagues at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran) for compiling, de-identifying, and openly sharing the Z-Alizadeh Sani coronary artery disease dataset through the UCI Machine Learning Repository and Mendeley Data. We also acknowledge the Database Center for Life Science (DBCLS, Japan) for open public access to the BodyParts3D anatomical polygon model database. The authors also appreciate the organizers of the IIT Mandi hackathon for originally highlighting cardiovascular prediction benchmarks as an open-access scientific challenge problem."*

- [ ] **Confirmed:** I approve this Acknowledgements statement.

---

## 5. Journal Submission Track & Publishing Model

Based on our editorial audit:
- **Primary Recommendation:** *Computer Methods and Programs in Biomedicine* (CMPB, Elsevier).
  - Published original dataset papers (Alizadehsani et al., 2013, 2018; Abdar et al., 2019).
  - Editorial scope perfectly matches multi-target clinical machine learning.
- **Publishing Model Selection:**
  - [ ] **Subscription Publishing (Recommended):** **\$0 APC (No fee to author)**. Elsevier publishes the paper behind standard academic subscription, accessible to all subscribing universities and institutions worldwide.
  - [ ] **Gold Open Access:** Requires payment of Article Processing Charge (APC approx. \$3,440 USD) upon paper acceptance.
