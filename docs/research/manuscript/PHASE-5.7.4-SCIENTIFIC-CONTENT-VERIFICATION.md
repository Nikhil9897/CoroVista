# CoroVista — Phase 5.7.4: Final Scientific Content & Submission Cleanup Report

**Date:** November 15, 2026  
**Auditor / Specialist:** Senior Biomedical ML Auditor & Journal Submission Specialist  
**Execution Objective:** Perform scientific reconciliation of RCA threshold metrics, correct abstract calibration wording for target-specific configurations, remove internal tracking material from the manuscript PDF, verify bibliography integrity, and validate canonical artifact identity.

---

## Executive Summary

Phase 5.7.4 executes the final scientific content and document-structure cleanup required for journal submission:
1. **RCA Threshold Metric Reconciliation:** An exhaustive mathematical and programmatic investigation was conducted across raw cross-validation predictions (`oof_y_true` and `oof_y_prob`). The discrepancy between Sensitivity $74.21\% \pm 10.64\%$ (fold-level) and $74.21\% \pm 2.53\%$ (repeat-level) was resolved: both are mathematically verified values representing distinct aggregation scopes (Protocol 3: 25 outer test folds vs. Protocol 4: 5 complete CV repeats). The abstract correctly retains the **25-fold outer-fold sample statistics (`ddof=1`)** to maintain strict methodological consistency with all other targets.
2. **Abstract Calibration Wording Corrected:** The abstract was revised to accurately state that **Cath, LAD, and RCA utilize Sigmoid (Platt) calibration**, whereas **LCX utilizes an uncalibrated selected production model**.
3. **Internal Tracking Material Removed:** The `Unresolved References Tracker & Author Confirmation Items` administrative section was removed from the manuscript PDF, leaving the **23 verified bibliography entries as the final section on Page 29**. All tracking items remain preserved in `docs/research/manuscript/PHASE-5.5-AUTHOR-CONFIRMATION-REQUIRED.md`.
4. **Canonical PDF Verified:** Both canonical copies (`./CoroVista-Research-Manuscript.pdf` and `./docs/research/manuscript/CoroVista-Research-Manuscript.pdf`) were updated, verified as **100% byte-identical** (SHA-256: `6b1210377ed3ee7d63f8e815947d39225ba599d6a3bfa90c62bf884c9c904c46`), and confirmed at **exactly 29 pages**.

---

## 1. Investigation of RCA Threshold Metric Discrepancies

### 1.1 Issue Context
The manuscript Abstract reports production operating threshold ($\tau = 0.35$) metrics for RCA:
$$\text{Sensitivity: } 74.21\% \pm 10.64\%, \quad \text{Specificity: } 57.48\% \pm 7.10\%$$
In contrast, an earlier entry in the Phase 5.5 verification report noted:
$$\text{Sensitivity: } 74.21\% \pm 2.53\%, \quad \text{Specificity: } 57.48\% \pm 1.69\%$$

### 1.2 Programmatic Investigation of Raw Predictions
The authoritative raw data were parsed directly from `data/reports/reproduction_audit/calibration_results.json` under `data["RCA"]["LogisticRegression_sigmoid"]`:
- Total concatenated out-of-fold predictions: $N_{\text{total}} = 1,515$ (5 repeats $\times$ 303 patients).
- Ground truth array: `oof_y_true` ($1,515$ elements).
- Calibrated probability array: `oof_y_prob` ($1,515$ elements).

Two distinct evaluation protocols were computed from these exact raw arrays:

#### Protocol 3: Fold-Level Aggregation (25 Outer Test Folds, $\tau = 0.35$)
- **Sample Unit:** Individual outer test folds ($N = 25$, partition sizes: $[61, 61, 61, 60, 60] \times 5$).
- **Computation:** Metrics are evaluated on each fold independently, then aggregated using sample mean and sample standard deviation ($ddof=1, N=25$):
  $$\bar{x}_{\text{fold}} = \frac{1}{25}\sum_{i=1}^{25} x_i, \quad s_{\text{fold}} = \sqrt{\frac{1}{24}\sum_{i=1}^{25}(x_i - \bar{x}_{\text{fold}})^2}$$
- **Raw Numerical Results:**
  - **Sensitivity:** $\text{Mean} = 0.742134$ (**$74.21\%$**), $\text{Sample SD } (ddof=1) = 0.106437$ (**$\pm 10.64\%$**), $\text{Pop SD } (ddof=0) = 0.104287$.
  - **Specificity:** $\text{Mean} = 0.574822$ (**$57.48\%$**), $\text{Sample SD } (ddof=1) = 0.070974$ (**$\pm 7.10\%$**), $\text{Pop SD } (ddof=0) = 0.069540$.
  - **Balanced Accuracy:** $\text{Mean} = 0.658478$ (**$65.85\%$**), $\text{Sample SD } (ddof=1) = 0.063849$ (**$\pm 6.38\%$**).
  - **$F_1$-Score:** $\text{Mean} = 0.605304$ (**$0.6053$**), $\text{Sample SD } (ddof=1) = 0.068407$ (**$\pm 0.0684$**).

#### Protocol 4: Repeat-Level Aggregation (5 Complete CV Repeats, $\tau = 0.35$)
- **Sample Unit:** Complete cohort resamplings ($R = 5$, cohort size per repeat: $N = 303$).
- **Computation:** Out-of-fold probabilities are assembled for all 303 patients for each complete repeat $r \in \{1, 2, 3, 4, 5\}$, evaluated against true labels, and the 5 resulting metrics are summarized using sample mean and sample standard deviation ($ddof=1, R=5$):
  - Repeat 1 ($N=303$): Sensitivity $= 0.745614$, Specificity $= 0.582011$
  - Repeat 2 ($N=303$): Sensitivity $= 0.780702$, Specificity $= 0.566138$
  - Repeat 3 ($N=303$): Sensitivity $= 0.719298$, Specificity $= 0.587302$
  - Repeat 4 ($N=303$): Sensitivity $= 0.719298$, Specificity $= 0.576720$
  - Repeat 5 ($N=303$): Sensitivity $= 0.745614$, Specificity $= 0.560847$
- **Raw Numerical Results:**
  - **Sensitivity:** $\text{Mean} = 0.742105$ (**$74.21\%$**), $\text{Sample SD } (ddof=1) = 0.025272$ (**$\pm 2.53\%$**), $\text{Pop SD } (ddof=0) = 0.022604$.
  - **Specificity:** $\text{Mean} = 0.574603$ (**$57.46\%$**), $\text{Sample SD } (ddof=1) = 0.010972$ (**$\pm 1.10\%$**), $\text{Pop SD } (ddof=0) = 0.009813$.
  - **Balanced Accuracy:** $\text{Mean} = 0.658354$ (**$65.84\%$**), $\text{Sample SD } (ddof=1) = 0.010193$ (**$\pm 1.02\%$**).
  - **$F_1$-Score:** $\text{Mean} = 0.606330$ (**$0.6063$**), $\text{Sample SD } (ddof=1) = 0.012033$ (**$\pm 0.0120$**).

### 1.3 Reconciliation Verdict & Reporting Standard
1. **Nature of the Discrepancy:** The values represent **two distinct aggregation scopes**, not an error in calculation:
   - $74.21\% \pm 10.64\%$ describes **fold-to-fold variability** ($N=25$).
   - $74.21\% \pm 2.53\%$ describes **repeat-to-repeat variability** across complete cohorts ($R=5$).
   - The narrower standard deviation ($\pm 2.53\%$ vs. $\pm 10.64\%$) arises because evaluating across $N=303$ patients averages out fold-partitioning sample variance.
   - The Phase 5.5 report figure for specificity ($\pm 1.69\%$) was an unverified manual transcription; the true repeat-level sample SD is **$\pm 1.10\%$** ($57.46\% \pm 1.10\%$).
2. **Which Values Belong in the Manuscript:**
   - **Abstract:** Must report the **25 outer-fold sample statistics (`ddof=1`)**:
     $$\text{Recall: } 74.21\% \pm 10.64\%, \quad \text{Specificity: } 57.48\% \pm 7.10\%$$
     This guarantees methodological uniformity with Cath ($0.9123 \pm 0.0404$), LAD ($0.8443 \pm 0.0528$), LCX ($0.7358 \pm 0.0629$), and RCA ($0.7163 \pm 0.0605$), all of which report 25 outer-fold sample standard deviations.
   - **Table 6 & Section 4.3:** Both Protocol 3 (25 outer folds) and Protocol 4 (5 complete repeats) are explicitly separated, tabulated, and defined to provide full statistical transparency.

---

## 2. Abstract Calibration Wording Revision

### 2.1 Deficiency in Previous Text
The previous draft generalized that "calibrated models demonstrated calibration reliability across all targets." However, Table 2 and Section 4.2 establish that **LCX uses an uncalibrated selected production model** (because Platt scaling degraded empirical calibration error on LCX).

### 2.2 Text Revisions Executed
The wording in `docs/research/manuscript/CoroVista-Research-Manuscript.md` (and `01-abstract-introduction-related-work.md`) was updated:

- **Methods:**
  - *Previous:* `...with partition-isolated preprocessing and Platt (Sigmoid) calibration.`
  - *Revised:* `...with partition-isolated preprocessing and target-specific calibration (Sigmoid Platt calibration for Cath, LAD, and RCA; uncalibrated for LCX).`
- **Results:**
  - *Previous:* `Calibrated models demonstrated strong multi-target discrimination and calibration reliability across 25 outer test folds (Mean ± Sample SD, ddof=1): Cath ROC-AUC 0.9123 ± 0.0404 ... LCX ROC-AUC 0.7358 ± 0.0629 ...`
  - *Revised:* `Selected production models demonstrated strong multi-target discrimination and calibration reliability across 25 outer test folds (Mean ± Sample SD, ddof=1): Cath (calibrated) ROC-AUC 0.9123 ± 0.0404 (Brier 0.1034 ± 0.0251, ECE 0.1004 ± 0.0227); LAD (calibrated) ROC-AUC 0.8443 ± 0.0528 (Brier 0.1609 ± 0.0226, ECE 0.1326 ± 0.0394); LCX (uncalibrated) ROC-AUC 0.7358 ± 0.0629 (Brier 0.2054 ± 0.0240, ECE 0.1366 ± 0.0315); and RCA (calibrated) ROC-AUC 0.7163 ± 0.0605 (Brier 0.2060 ± 0.0150, ECE 0.1000 ± 0.0321).`
- **Conclusions:**
  - *Previous:* `Calibrated vessel-level prediction and systematic stability profiling represent essential prerequisites...`
  - *Revised:* `Target-specific probability calibration and systematic stability profiling represent essential prerequisites for trustworthy clinical decision support.`

All verified numerical results, standard deviations, and downstream conclusions remain intact.

---

## 3. Removal of Internal Tracking Material from PDF

### 3.1 Content Removed
The trailing markdown block at the conclusion of `CoroVista-Research-Manuscript.md`:
```markdown
#### Unresolved References Tracker & Author Confirmation Items
- `[RESOLVED in Phase 5.5]` (Section 1.1): Elective catheterization diagnostic yield verified and cited via Patel et al. (2010, NEJM; DOI: 10.1056/NEJMoa0907272).
- `[UNRESOLVED AUTHOR CONFIRMATION ITEM]` (Section 3.1 & Declarations): Historical Institutional Review Board / Ethics Committee approval protocol identifier for the primary 2011–2013 data collection at Shaheed Rajaei Cardiovascular, Medical and Research Center. (Documented in `docs/research/manuscript/PHASE-5.5-AUTHOR-CONFIRMATION-REQUIRED.md`).
```
was completely removed from the manuscript text.

### 3.2 Audit of Final Page 29
- The manuscript PDF terminates cleanly with **Reference [23] (Visani et al., 2022)**.
- **Zero internal tracking boxes, draft confirmation tags, or unresolved item headers appear on Page 29.**
- All author confirmation items remain cataloged in the standalone reference document:
  [`docs/research/manuscript/PHASE-5.5-AUTHOR-CONFIRMATION-REQUIRED.md`](file:///Users/apple/Desktop/Namandeep%20Tripathi/My%20Projects/CoroVista/docs/research/manuscript/PHASE-5.5-AUTHOR-CONFIRMATION-REQUIRED.md).

---

## 4. Final Quality Assurance & Artifact Identity

| Metric / Check | Required Standard | Verified Finding | Status |
|---|---|---|:---:|
| **Page Count** | Exactly 29 pages | **29 pages** | **PASS** |
| **Page 1 Layout** | Approved cover layout | Title, authors, structured abstract, keywords; 0 draft labels; 97 pt buffer to margin | **PASS** |
| **Page 13 Layout** | Dedicated Landscape Table 2 | $841.89 \times 595.28$ pt, 770 pt table width, 8.2/8.0 pt typography, 8.0 pt padding | **PASS** |
| **Page 29 Layout** | Final References Section | References [1]–[23] present; Brier (1950) DOI intact; zero tracking boxes | **PASS** |
| **Running Headers** | Pages 2–29 clean title | `"CoroVista: Reliable & Explainable CAD Prediction"` on 28/28 body pages | **PASS** |
| **Running Footers** | Pages 2–29 disclaimer | `"CoroVista Research Manuscript — Not for Clinical Diagnostic Use"` on 28/28 body pages | **PASS** |
| **Brier 1950 DOI** | Complete DOI without truncation | `10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2` intact | **PASS** |
| **File Byte Identity** | Root PDF == Docs PDF | Both files are **2,119,385 bytes**; SHA-256 match | **PASS** |

### Canonical Artifact Checksums

- **File 1 (Root):**
  `/Users/apple/Desktop/Namandeep Tripathi/My Projects/CoroVista/CoroVista-Research-Manuscript.pdf`  
  *Size:* 2,119,385 bytes | *SHA-256:* `6b1210377ed3ee7d63f8e815947d39225ba599d6a3bfa90c62bf884c9c904c46`
- **File 2 (Docs):**
  `/Users/apple/Desktop/Namandeep Tripathi/My Projects/CoroVista/docs/research/manuscript/CoroVista-Research-Manuscript.pdf`  
  *Size:* 2,119,385 bytes | *SHA-256:* `6b1210377ed3ee7d63f8e815947d39225ba599d6a3bfa90c62bf884c9c904c46`

---

## 5. Verification Commands for Quality Control

To reproduce the verification checks independently:

```bash
# 1. Check exact 29 pages, file sizes, and SHA-256 hash match
./.venv/bin/python3 -c "
import pypdfium2 as pdfium, os, hashlib
for p in ['CoroVista-Research-Manuscript.pdf', 'docs/research/manuscript/CoroVista-Research-Manuscript.pdf']:
    doc = pdfium.PdfDocument(p)
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    print(f'{p}: {len(doc)} pages, {os.path.getsize(p):,} bytes, SHA: {h}')
"

# 2. Verify all 23 references on Page 29 and absence of tracking material
./.venv/bin/python3 -c "
import pypdfium2 as pdfium
doc = pdfium.PdfDocument('CoroVista-Research-Manuscript.pdf')
p29 = doc[28].get_textpage().get_text_range()
assert 'Unresolved References Tracker' not in p29, 'Found tracker on Page 29!'
assert all(f'[{i}]' in p29 for i in range(1, 24)), 'Missing references on Page 29!'
assert '10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2' in p29, 'Corrupted Brier DOI!'
print('Page 29 verified: clean 23 references, zero tracking material.')
"

# 3. Verify target-specific calibration wording on Page 1
./.venv/bin/python3 -c "
import pypdfium2 as pdfium
doc = pdfium.PdfDocument('CoroVista-Research-Manuscript.pdf')
p1 = doc[0].get_textpage().get_text_range()
assert 'target-specific calibration' in p1
assert 'LCX (uncalibrated)' in p1
assert 'Target-specific probability calibration' in p1
print('Page 1 verified: target-specific calibration accurately documented.')
"
```

---

## 6. Audit Sign-Off

- **Investigation Status:** COMPLETED.
- **RCA Discrepancy:** RECONCILED (Protocol 3 fold-level vs. Protocol 4 repeat-level).
- **Abstract Calibration Wording:** CORRECTED (LCX explicitly uncalibrated; Cath, LAD, RCA sigmoid calibrated).
- **Internal Tracker:** REMOVED from PDF; preserved in formal author confirmation document.
- **Artifact Status:** Publication-ready canonical PDF (29 pages).
