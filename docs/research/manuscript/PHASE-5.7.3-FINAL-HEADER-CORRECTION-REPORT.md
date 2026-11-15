# CoroVista — Phase 5.7.3: Final Header & Table Layout Correction Report

**Date:** November 15, 2026  
**Auditor / Specialist:** Senior Biomedical ML Auditor & Manuscript Production Specialist  
**Execution Objective:** Remove all remaining draft/confidential running headers, replace them with a neutral running title, improve the layout and numerical readability of Table 2 on the dedicated landscape page, and verify the resulting 29-page PDF artifact.

---

## Executive Summary

Following manual visual inspection of the 29-page manuscript PDF, two targeted corrections were requested:
1. **Running Headers:** The residual phrase `"Working Review Draft — Confidential"` displayed on pages 2–29 was removed and replaced with the clean, neutral header `"CoroVista: Reliable & Explainable CAD Prediction"`. The clinical diagnostic disclaimer footer was strictly retained.
2. **Table 2 on Dedicated Landscape Page (Page 13):** Table width was increased to 770 pt to fill the landscape printable area; font sizes and cell padding were increased to improve numerical legibility; excessive vertical and horizontal whitespace was eliminated while preserving every number, column, caption, and SD notation within page margins.
3. **Approved Content Preservation:** Page 1 title-and-abstract layout was left untouched; no scientific metrics, equations, figures, references, or text were altered. Page count remains **exactly 29 pages**.

Prior to modifying the canonical files, the Phase 5.7 canonical PDF was backed up to the archive directory.

---

## 1. Canonical Artifact Inventory & Integrity

| # | File Path | File Size | Modification Time (UTC) | Page Count | SHA-256 Hash | Status |
|---|---|---|---|:---:|---|---|
| **1** | `CoroVista-Research-Manuscript.pdf` (Root) | 2,119,879 bytes | 2026-11-15T17:18:52Z | **29** | `cdc0d6cc03d9307a320876e1311dc32652e0fedec3ea0b188d925bfa71767b99` | **Updated Canonical** |
| **2** | `docs/research/manuscript/CoroVista-Research-Manuscript.pdf` (Docs) | 2,119,879 bytes | 2026-11-15T17:18:52Z | **29** | `cdc0d6cc03d9307a320876e1311dc32652e0fedec3ea0b188d925bfa71767b99` | **Updated Canonical** |
| **3** | `docs/research/manuscript/archive/CoroVista-Research-Manuscript-phase5.7-backup.pdf` | 2,121,429 bytes | 2026-11-15T17:17:26Z | **29** | `7c7c61f8b3530473f818eacaf17183bcbd78bea93d69ae8711e9a23cb764189b` | Pre-Correction Backup |
| **4** | `docs/research/manuscript/archive/CoroVista-Research-Manuscript-phase5.7-root-backup.pdf` | 2,121,429 bytes | 2026-11-15T17:17:26Z | **29** | `7c7c61f8b3530473f818eacaf17183bcbd78bea93d69ae8711e9a23cb764189b` | Pre-Correction Backup |

- Both canonical files (`./CoroVista-Research-Manuscript.pdf` and `./docs/research/manuscript/CoroVista-Research-Manuscript.pdf`) are **100% byte-identical** (SHA-256: `cdc0d6cc03d9307a320876e1311dc32652e0fedec3ea0b188d925bfa71767b99`).
- No competing or alternate filenames were generated.

---

## 2. Running Header & Footer Audit Across All 29 Pages

Every page was scanned using `pypdfium2` text stream analysis.

### 2.1 Audit Results:
- **"Working Review Draft" occurrences:** **0** (eliminated from all 29 pages).
- **"Confidential" occurrences:** **0** (eliminated from all 29 pages).
- **Page 1 Layout:**
  - Running header: Completely suppressed (no top header or separator rule).
  - Footer: Clean `Page 1 of 29` aligned to the right with 0.5 pt rule.
  - Zero draft labels, zero metadata boxes, zero fake emails or dummy ORCIDs.
- **Pages 2–29 Running Headers:**
  - String: `"CoroVista: Reliable & Explainable CAD Prediction"`
  - Typography: 7.5 pt bold, navy `#1e3a8a`, left-aligned at `LEFT_MARGIN` ($x = 36$ pt).
  - Right string: Blank (no draft labels, no confidentiality tags).
  - Separator rule: 0.5 pt `#cbd5e1` spanning full content width ($x = 36$ pt to $w - 36$ pt).
  - Verified present on **28 of 28 body pages** (100% compliance).
- **Pages 2–29 Running Footers:**
  - Left string: `"CoroVista Research Manuscript — Not for Clinical Diagnostic Use"` (7.5 pt regular slate `#64748b`).
  - Right string: `"Page X of 29"` (7.5 pt bold dark slate `#1e293b`).
  - Separator rule: 0.5 pt `#cbd5e1` at $y = 34$ pt.
  - Verified present on **28 of 28 body pages** (100% compliance).

---

## 3. Table 2 Improvement on Dedicated Landscape Page (Page 13)

### 3.1 Layout & Readability Upgrades

| Parameter | Phase 5.7 (Previous) | Phase 5.7.3 (Updated) | Enhancement |
|---|---|---|---|
| **Page Dimensions** | $841.89 \times 595.28$ pt (Landscape) | $841.89 \times 595.28$ pt (Landscape) | Preserved dedicated landscape geometry |
| **Table Width** | 760.0 pt | **770.0 pt** | Expands to full margin-to-margin printable area ($841.89 - 72.0 \approx 770$ pt) |
| **Header Font & Leading** | 7.5 pt / 9.5 pt | **8.2 pt / 10.8 pt** | +0.7 pt font increase; crisp readability |
| **Data Cell Font & Leading** | 7.2 pt / 9.2 pt | **8.0 pt / 10.6 pt** | +0.8 pt font increase; balanced vertical hierarchy |
| **Vertical Cell Padding** | 4.0 pt top / 4.0 pt bottom | **8.0 pt top / 8.0 pt bottom** | Doubled cell padding; eliminates cramped aesthetic |
| **Horizontal Cell Padding** | 4.0 pt left / 4.0 pt right | **4.0 pt left / 4.0 pt right** | Maintained optimal column boundary buffer |
| **Table Title Style** | 10 pt bold / 13 pt leading | **11 pt bold / 14 pt leading** | Prominent section header hierarchy |
| **Table Notes Style** | 7.5 pt italic / 10 pt leading | **8.0 pt italic / 11 pt leading** | Legible methodology and provenance captions |
| **Vertical Whitespace** | Excessive empty bottom void (~350 pt) | **Balanced distribution** | Larger fonts, generous padding, and spacers reduce void by ~85 pt |

### 3.2 Exact Column Width Breakdown (Total = 770.0 pt)

1. **Target:** 48.0 pt (Left aligned)
2. **Clinical Endpoint:** 118.0 pt (Left aligned)
3. **Selected Model:** 80.0 pt (Center aligned)
4. **Preprocessing:** 92.0 pt (Center aligned)
5. **Calibration Method:** 80.0 pt (Center aligned)
6. **Operating Cutoff ($\tau$):** 48.0 pt (Center aligned)
7. **ROC-AUC (Mean $\pm$ SD):** 76.0 pt (Center aligned)
8. **PR-AUC (Mean $\pm$ SD):** 76.0 pt (Center aligned)
9. **Brier Score (Mean $\pm$ SD):** 76.0 pt (Center aligned)
10. **ECE (Mean $\pm$ SD):** 76.0 pt (Center aligned)

### 3.3 Preserved Scientific Values & Conventions
All data cells strictly preserve two clean vertical lines:
- **Line 1:** Primary cross-fold **Mean $\pm$ sample SD (`ddof=1`)** in bold `#0f172a`.
- **Line 2:** Secondary **population SD (`ddof=0`)** in grey bracketed notation `[0.0xxx ddof=0]`.

| Target | Model | Calibration | Cutoff | ROC-AUC (Mean $\pm$ SD) | PR-AUC (Mean $\pm$ SD) | Brier Score (Mean $\pm$ SD) | ECE (Mean $\pm$ SD) |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| **Cath** | XGBoost | Sigmoid (Platt) | 0.50 | **$0.9123 \pm 0.0404$**<br>`[0.0396 ddof=0]` | **$0.9597 \pm 0.0200$**<br>`[0.0196 ddof=0]` | **$0.1034 \pm 0.0251$**<br>`[0.0246 ddof=0]` | **$0.1004 \pm 0.0227$**<br>`[0.0222 ddof=0]` |
| **LAD** | XGBoost | Sigmoid (Platt) | 0.50 | **$0.8443 \pm 0.0528$**<br>`[0.0518 ddof=0]` | **$0.8818 \pm 0.0471$**<br>`[0.0462 ddof=0]` | **$0.1609 \pm 0.0226$**<br>`[0.0221 ddof=0]` | **$0.1326 \pm 0.0394$**<br>`[0.0386 ddof=0]` |
| **LCX** | XGBoost | Uncalibrated | 0.50 | **$0.7358 \pm 0.0629$**<br>`[0.0616 ddof=0]` | **$0.6173 \pm 0.0838$**<br>`[0.0821 ddof=0]` | **$0.2054 \pm 0.0240$**<br>`[0.0235 ddof=0]` | **$0.1366 \pm 0.0315$**<br>`[0.0309 ddof=0]` |
| **RCA** | Logistic Regression | Sigmoid (Platt) | 0.35 | **$0.7163 \pm 0.0605$**<br>`[0.0593 ddof=0]` | **$0.6098 \pm 0.0775$**<br>`[0.0759 ddof=0]` | **$0.2060 \pm 0.0150$**<br>`[0.0147 ddof=0]` | **$0.1000 \pm 0.0321$**<br>`[0.0315 ddof=0]` |

---

## 4. Content Preservation Verification

1. **Page 1 Cover Layout:**
   - Retained 100% of the approved layout: Title, authors `Naman Deep Tripathi, Nikhil Agrawal`, structured Abstract (`Background`, `Methods`, `Results`, `Conclusions`), and Keywords.
   - Zero administrative boxes, zero unverified affiliations, zero fake contact info.
2. **Page 2 Start:**
   - Section 1 (*Introduction*) begins at the top margin of Page 2.
3. **Reference Formatting (Page 29):**
   - Reference [8] (Brier 1950) intact with valid, complete DOI:
     ```text
     [8] Brier, G. W. (1950). Verification of forecasts expressed in terms of probability.
     Monthly Weather Review, 78(1), 1–3. DOI: 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2
     ```
   - All 23 references verified with zero syntax drops or truncated characters.
4. **Author Confirmation Box:**
   - Final audit statement preserved at the foot of Page 29.
5. **Exact Page Count:**
   - Total pages: **exactly 29 pages**.

---

## 5. Verification Commands for Quality Assurance

To independently audit the final generated artifact, run:

```bash
# 1. Verify byte identity and exact 29-page count
./.venv/bin/python3 -c "
import pypdfium2 as pdfium, os, hashlib
for p in ['CoroVista-Research-Manuscript.pdf', 'docs/research/manuscript/CoroVista-Research-Manuscript.pdf']:
    doc = pdfium.PdfDocument(p)
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    print(f'{p}: {len(doc)} pages, {os.path.getsize(p):,} bytes, SHA: {h}')
"

# 2. Verify complete absence of draft / confidential running headers
./.venv/bin/python3 -c "
import pypdfium2 as pdfium
doc = pdfium.PdfDocument('CoroVista-Research-Manuscript.pdf')
for pno in range(len(doc)):
    text = doc[pno].get_textpage().get_text_range()
    assert 'Working Review Draft' not in text, f'Failed on page {pno+1}'
    assert 'Confidential' not in text, f'Failed on page {pno+1}'
print('All 29 pages verified 100% free of draft/confidential labels.')
"

# 3. Verify clean running header on Pages 2-29
./.venv/bin/python3 -c "
import pypdfium2 as pdfium
doc = pdfium.PdfDocument('CoroVista-Research-Manuscript.pdf')
for pno in range(1, 29):
    text = doc[pno].get_textpage().get_text_range()
    assert 'CoroVista: Reliable & Explainable CAD Prediction' in text, f'Missing header on page {pno+1}'
    assert 'CoroVista Research Manuscript — Not for Clinical Diagnostic Use' in text, f'Missing footer on page {pno+1}'
print('Pages 2-29 verified with clean running title and clinical disclaimer footer.')
"

# 4. Open directly in macOS Preview to visually inspect
open "/Users/apple/Desktop/Namandeep Tripathi/My Projects/CoroVista/CoroVista-Research-Manuscript.pdf"
```

---

## 6. Audit Sign-Off

- **Corrections Executed:** Running header cleaned; Table 2 enlarged and restyled; whitespace balanced.
- **Scientific Integrity:** 100% preserved. Zero modifications to numbers, methods, references, or figures.
- **Artifact Status:** Publication-ready, verified 29-page PDF.
