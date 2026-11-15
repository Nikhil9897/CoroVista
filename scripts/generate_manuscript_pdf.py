#!/usr/bin/env python3
"""
CoroVista Manuscript PDF Generator (Phase 5.7 Refined)
======================================================
Generates a publication-quality scientific PDF manuscript from:
    docs/research/manuscript/CoroVista-Research-Manuscript.md

Phase 5.7 Refinements:
- Dedicated, visually clean academic Title & Abstract page (Page 1) without administrative clutter
- Introduction starts cleanly on Page 2
- Table 2 rendered on a dedicated Landscape page (760 pt wide) with uncompressed columns, readable headings, and proper <br/> line breaks preserving mean ± sample SD and population SD
- Robust Markdown link parser handling balanced parentheses and URL-encoded DOIs (e.g., Brier 1950)
- TrueType Arial font family for full Unicode support (Greek, mathematical operators, Polish diacritics)
- Dynamic two-pass header & footer adapting to portrait and landscape orientations ("Page X of 29")
- Exact numerical and scientific text preservation across all 12 tables, 6 figures, 15 equations, and 23 references

Usage:
    MPLCONFIGDIR=/tmp ./.venv/bin/python scripts/generate_manuscript_pdf.py
"""

import os
import sys
import re
import io
import html
import shutil
from PIL import Image as PILImage
import pypdfium2 as pdfium

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ReportLab imports
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    PageBreak,
    NextPageTemplate,
    HRFlowable,
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TrueType Arial family for full Unicode support (Polish, Greek, Math)
FONT_FAMILY = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"
FONT_BOLDITALIC = "Helvetica-BoldOblique"

arial_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
arial_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
arial_italic = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
arial_bolditalic = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"

if os.path.exists(arial_path) and os.path.exists(arial_bold):
    pdfmetrics.registerFont(TTFont("Arial", arial_path))
    pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold))
    pdfmetrics.registerFont(TTFont("Arial-Italic", arial_italic if os.path.exists(arial_italic) else arial_path))
    pdfmetrics.registerFont(TTFont("Arial-BoldItalic", arial_bolditalic if os.path.exists(arial_bolditalic) else arial_bold))
    FONT_FAMILY = "Arial"
    FONT_BOLD = "Arial-Bold"
    FONT_ITALIC = "Arial-Italic"
    FONT_BOLDITALIC = "Arial-BoldItalic"
    print("Using Arial TTF font with comprehensive Unicode support.")
else:
    print("Using standard Helvetica PostScript font.")

# Define paths
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MD_PATH = os.path.join(WORKSPACE_DIR, "docs/research/manuscript/CoroVista-Research-Manuscript.md")
PDF_OUT_MANUSCRIPT = os.path.join(WORKSPACE_DIR, "docs/research/manuscript/CoroVista-Research-Manuscript.pdf")
PDF_OUT_ROOT = os.path.join(WORKSPACE_DIR, "CoroVista-Research-Manuscript.pdf")

# Page dimensions (A4: 595.27 x 841.89 pt, Landscape: 841.89 x 595.27 pt)
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 36.0    # 0.5 in
RIGHT_MARGIN = 36.0   # 0.5 in
TOP_MARGIN = 44.0
BOTTOM_MARGIN = 44.0
PORTRAIT_CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN    # 523.27 pt
PORTRAIT_CONTENT_HEIGHT = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN  # 753.89 pt

LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT = landscape(A4)
LANDSCAPE_CONTENT_WIDTH = LANDSCAPE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN    # 769.89 pt
LANDSCAPE_CONTENT_HEIGHT = LANDSCAPE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN  # 507.27 pt

# Figure mapping
FIGURE_MAP = {
    1: os.path.join(WORKSPACE_DIR, "data/reports/reproduction_audit/plots/roc_curves.png"),
    2: os.path.join(WORKSPACE_DIR, "data/reports/reproduction_audit/plots/calibration_curves.png"),
    3: os.path.join(WORKSPACE_DIR, "data/reports/phase4/summary/figures/cross_target_shap_stability.png"),
    4: os.path.join(WORKSPACE_DIR, "data/reports/phase4/summary/figures/cross_target_prediction_stability.png"),
    5: os.path.join(WORKSPACE_DIR, "data/reports/phase4/uncertainty/cath/figures/uncertainty_distributions.png"),
    6: os.path.join(WORKSPACE_DIR, "data/reports/phase4/robustness/cath/figures/feature_ablation_comparison.png"),
}


class DynamicNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic running header and 'Page X of Y' footer adapting to orientation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        w, h = self._pagesize

        # Page 1: Clean academic journal title-and-abstract page
        if self._pageNumber == 1:
            # Suppress running header completely
            # Clean bottom page number only (no draft / confidential labels on page 1)
            self.setFont(FONT_FAMILY, 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(w - RIGHT_MARGIN, 24, f"Page {self._pageNumber} of {page_count}")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(LEFT_MARGIN, 34, w - RIGHT_MARGIN, 34)
            self.restoreState()
            return

        # Running header: Pages > 1
        self.setFont(FONT_BOLD, 7.5)
        self.setFillColor(colors.HexColor("#1e3a8a"))
        self.drawString(LEFT_MARGIN, h - 28, "CoroVista: Reliable & Explainable CAD Prediction")
        
        # Header rule
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(LEFT_MARGIN, h - 32, w - RIGHT_MARGIN, h - 32)

        # Running footer: Pages > 1
        self.setFont(FONT_FAMILY, 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(LEFT_MARGIN, 24, "CoroVista Research Manuscript — Not for Clinical Diagnostic Use")
        
        self.setFont(FONT_BOLD, 7.5)
        self.setFillColor(colors.HexColor("#1e293b"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(w - RIGHT_MARGIN, 24, page_str)
        
        # Footer rule
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(LEFT_MARGIN, 34, w - RIGHT_MARGIN, 34)

        self.restoreState()


def convert_inline_math(m_str):
    """Converts LaTeX inline math to clean Unicode and HTML tags."""
    s = m_str.strip()
    s = re.sub(r"\\text\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\mathbf\{([^}]+)\}", r"\1", s)
    s = s.replace(r"\pm", "±")
    s = s.replace(r"\ge", "≥")
    s = s.replace(r"\le", "≤")
    s = s.replace(r"\times", "×")
    s = s.replace(r"\cdot", "·")
    s = s.replace(r"\approx", "≈")
    s = s.replace(r"\ne", "≠")
    s = s.replace(r"\in", "∈")
    s = s.replace(r"\forall", "∀")
    s = s.replace(r"\infty", "∞")
    s = s.replace(r"\mid", "|")
    s = s.replace(r"\quad", " ")
    s = s.replace(r"\qquad", "  ")
    s = s.replace(r"\%", "%")
    s = s.replace(r"\tau", "τ")
    s = s.replace(r"\sigma", "σ")
    s = s.replace(r"\rho", "ρ")
    s = s.replace(r"\mu", "μ")
    s = s.replace(r"\alpha", "α")
    s = s.replace(r"\beta", "β")
    s = s.replace(r"\Delta", "Δ")
    s = s.replace(r"\phi", "φ")
    s = s.replace(r"\lambda", "λ")
    s = s.replace(r"\sum", "∑")
    s = s.replace(r"\sqrt", "√")
    s = s.replace(r"\binom{25}{2}", "C(25,2)")
    
    # Handle fractions
    s = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1 / \2)", s)
    
    # Handle braces _{...} and ^{...}
    s = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", s)
    
    # Handle simple unbraced ^ and _
    s = re.sub(r"\^([a-zA-Z0-9\+\-]+)", r"<sup>\1</sup>", s)
    s = re.sub(r"_([a-zA-Z0-9\+\-]+)", r"<sub>\1</sub>", s)
    
    # Prevent nested tags
    s = re.sub(r"<sup>(.*?)<sub>(.*?)</sub>(.*?)</sup>", r"<sup>\1\2\3</sup>", s)
    s = re.sub(r"<sub>(.*?)<sup>(.*?)</sup>(.*?)</sub>", r"<sub>\1\2\3</sub>", s)
    
    # Remove any stray backslashes
    s = s.replace("\\", "")
    return s


def format_markdown_text(text):
    """Formats markdown text into ReportLab HTML-like paragraph markup."""
    # 0. Preserve HTML breaks (<br>, <br/>, <br />) before escaping
    text = re.sub(r"<br\s*/?>", "__HTML_BR__", text, flags=re.IGNORECASE)

    # 1. Replace inline math $...$ with placeholders
    math_placeholders = []
    def math_repl(m):
        idx = len(math_placeholders)
        conv = convert_inline_math(m.group(1))
        math_placeholders.append(conv)
        return f"__MATH_{idx}__"
    text = re.sub(r"\$([^\$\n]+)\$", math_repl, text)

    # 2. Replace inline code `...` with placeholders
    code_placeholders = []
    def code_repl(m):
        idx = len(code_placeholders)
        raw = m.group(1)
        safe = html.escape(raw)
        code_placeholders.append(f'<font name="Courier" size="7.5" color="#0369a1"><b>{safe}</b></font>')
        return f"__CODE_{idx}__"
    text = re.sub(r"`([^`]+)`", code_repl, text)

    # 3. Replace markdown links [text](url) with placeholders - supports balanced parentheses in URLs
    link_placeholders = []
    link_pattern = r"\[([^\]]+)\]\((https?://(?:[^\s\(\)]|\([^\s\(\)]*\))+)\)"
    def link_repl(m):
        idx = len(link_placeholders)
        lt = m.group(1)
        lu = m.group(2)
        # Percent-encode < and > in URL
        clean_lu = lu.replace("<", "%3C").replace(">", "%3E")
        safe_lu = html.escape(clean_lu)
        link_placeholders.append((lt, safe_lu))
        return f"__LINK_{idx}__"
    text = re.sub(link_pattern, link_repl, text)

    # 4. Escape raw XML characters (&, <, >)
    text = re.sub(r"&(?!([a-zA-Z0-9#]+;))", "&amp;", text)
    text = text.replace("<", "&lt;").replace(">", "&gt;")

    # 5. Bold & Italic
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)

    # 6. Restore links
    for idx, (lt, lu) in enumerate(link_placeholders):
        formatted_lt = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", lt)
        formatted_lt = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", formatted_lt)
        formatted_lt = formatted_lt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace(f"__LINK_{idx}__", f'<link href="{lu}" color="#1d4ed8"><u>{formatted_lt}</u></link>')

    # 7. Restore code
    for idx, c_html in enumerate(code_placeholders):
        text = text.replace(f"__CODE_{idx}__", c_html)

    # 8. Restore math
    for idx, m_html in enumerate(math_placeholders):
        text = text.replace(f"__MATH_{idx}__", m_html)

    # 9. Restore HTML break tags
    text = text.replace("__HTML_BR__", "<br/>")

    return text


def split_markdown_table_row(line):
    """Splits a markdown table row by '|' while protecting pipes inside math $...$ or code `...`."""
    placeholders = []
    def math_repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__MATH_P_{idx}__"
    
    s = re.sub(r"\$([^\$\n]+)\$", math_repl, line)
    s = re.sub(r"`([^`]+)`", math_repl, s)
    raw_cells = [c.strip() for c in s.split("|")[1:-1]]
    
    final_cells = []
    for c in raw_cells:
        for idx, orig in enumerate(placeholders):
            c = c.replace(f"__MATH_P_{idx}__", orig)
        final_cells.append(c)
    return final_cells


def render_equation_to_flowable(latex_str, eq_num=None, content_w=PORTRAIT_CONTENT_WIDTH):
    """Renders a LaTeX display equation using Matplotlib mathtext into an Image flowable."""
    fig = plt.figure(figsize=(7, 0.8))
    fig.text(0.5, 0.5, f"${latex_str.strip()}$", fontsize=11, ha="center", va="center")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=250, bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    
    pil_im = PILImage.open(buf)
    w_px, h_px = pil_im.size
    dpi = 250.0
    w_pt = w_px * 72.0 / dpi
    h_pt = h_px * 72.0 / dpi
    
    max_w = content_w - 40
    if w_pt > max_w:
        ratio = max_w / w_pt
        w_pt = max_w
        h_pt = h_pt * ratio

    buf.seek(0)
    img_flowable = Image(buf, width=w_pt, height=h_pt)
    img_flowable.hAlign = "CENTER"
    
    if eq_num is not None:
        num_para = Paragraph(f'<font size="8" color="#64748b">({eq_num})</font>', ParagraphStyle("EqNum", fontName=FONT_FAMILY, alignment=TA_RIGHT))
        eq_table = Table([[img_flowable, num_para]], colWidths=[content_w - 40, 40])
        eq_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]))
        return eq_table
    return img_flowable


def build_pdf():
    print(f"Reading source manuscript from: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Extract figure captions from Section 4.9
    fig_captions = {}
    pattern = r"#### Figure (\d+):([^\n]+)\n\*\*Caption:\*\*([^\n]+(?:\n(?!\n|####|---)[^\n]+)*)"
    for m in re.finditer(pattern, md_text):
        num = int(m.group(1))
        title = m.group(2).strip()
        cap = m.group(3).strip()
        fig_captions[num] = (title, cap)
    print(f"Loaded {len(fig_captions)} figure captions.")

    # Initialize typography styles
    title_style = ParagraphStyle(
        "AcademicTitle",
        fontName=FONT_BOLD,
        fontSize=19.5,
        leading=24,
        textColor=colors.HexColor("#0f2942"),
        alignment=TA_LEFT,
        spaceAfter=12,
    )
    author_style = ParagraphStyle(
        "AcademicAuthors",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_LEFT,
        spaceAfter=14,
    )
    abstract_heading_style = ParagraphStyle(
        "AbstractHeading",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e3a8a"),
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=8,
    )
    abstract_body_style = ParagraphStyle(
        "AbstractBody",
        fontName=FONT_FAMILY,
        fontSize=8.8,
        leading=12.8,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    abstract_kw_style = ParagraphStyle(
        "AbstractKeywords",
        fontName=FONT_FAMILY,
        fontSize=8.4,
        leading=12.0,
        textColor=colors.HexColor("#334155"),
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        fontName=FONT_BOLD,
        fontSize=13.5,
        leading=17,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        "SectionH3",
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )
    h4_style = ParagraphStyle(
        "SectionH4",
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#475569"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        fontName=FONT_FAMILY,
        fontSize=8.5,
        leading=11.8,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_JUSTIFY,
        spaceAfter=5,
    )
    bullet_style = ParagraphStyle(
        "BulletDark",
        fontName=FONT_FAMILY,
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#0f172a"),
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3,
    )
    numbered_style = ParagraphStyle(
        "NumberedDark",
        fontName=FONT_FAMILY,
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#0f172a"),
        leftIndent=16,
        firstLineIndent=-12,
        spaceAfter=3,
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        fontName=FONT_FAMILY,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )
    fig_title_style = ParagraphStyle(
        "FigTitle",
        fontName=FONT_BOLD,
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=2,
    )
    fig_cap_style = ParagraphStyle(
        "FigCaption",
        fontName=FONT_FAMILY,
        fontSize=7.5,
        leading=10.0,
        textColor=colors.HexColor("#334155"),
        alignment=TA_JUSTIFY,
    )
    table_title_style = ParagraphStyle(
        "TableTitle",
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )
    table_note_style = ParagraphStyle(
        "TableNote",
        fontName=FONT_ITALIC,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=4,
        keepWithNext=True,
    )
    ref_style = ParagraphStyle(
        "RefDark",
        fontName=FONT_FAMILY,
        fontSize=7.5,
        leading=10.2,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=16,
        firstLineIndent=-16,
        spaceAfter=4,
    )
    dec_h2_style = ParagraphStyle(
        "DecH2",
        parent=h2_style,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )
    dec_body_style = ParagraphStyle(
        "DecBody",
        parent=body_style,
        fontSize=8.3,
        leading=11.3,
        spaceAfter=3,
    )
    dec_bullet_style = ParagraphStyle(
        "DecBullet",
        parent=bullet_style,
        fontSize=8.1,
        leading=11.0,
        spaceAfter=2,
    )

    story = []

    # =========================================================================
    # TASK 1: CLEAN ACADEMIC TITLE & ABSTRACT PAGE (PAGE 1)
    # Contains ONLY: Title, Author names, verified author info (no fake placeholders),
    # complete Abstract (Background, Methods, Results, Conclusions), Keywords.
    # No administrative banners, no draft boxes, no metadata grids.
    # =========================================================================
    story.append(Paragraph("Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness", title_style))
    story.append(Paragraph("Naman Deep Tripathi, Nikhil Agrawal", author_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=10))

    # Extract Abstract Content
    abstract_match = re.search(r"## Abstract\s+### Background\s+([\s\S]+?)\s+### Methods\s+([\s\S]+?)\s+### Results\s+([\s\S]+?)\s+### Conclusions\s+([\s\S]+?)\s+\*\*Keywords:\*\*\s+([^\n]+)", md_text)
    if abstract_match:
        bg_text = format_markdown_text(abstract_match.group(1).strip())
        meth_text = format_markdown_text(abstract_match.group(2).strip())
        res_text = format_markdown_text(abstract_match.group(3).strip())
        conc_text = format_markdown_text(abstract_match.group(4).strip())
        kw_text = format_markdown_text(abstract_match.group(5).strip())

        story.append(Paragraph("ABSTRACT", abstract_heading_style))
        story.append(Paragraph(f"<b>Background:</b> {bg_text}", abstract_body_style))
        story.append(Paragraph(f"<b>Methods:</b> {meth_text}", abstract_body_style))
        story.append(Paragraph(f"<b>Results:</b> {res_text}", abstract_body_style))
        story.append(Paragraph(f"<b>Conclusions:</b> {conc_text}", abstract_body_style))
        story.append(Paragraph(f"<b>Keywords:</b> {kw_text}", abstract_kw_style))
    else:
        print("Warning: Abstract regex match failed!")

    # Start Introduction cleanly on Page 2
    story.append(PageBreak())

    # =========================================================================
    # PARSE DOCUMENT BODY (FROM SECTION 1 ONWARDS)
    # =========================================================================
    intro_start = md_text.find("## 1. Introduction")
    if intro_start == -1:
        intro_start = md_text.find("## Introduction")
    body_markdown = md_text[intro_start:]

    lines = body_markdown.splitlines()
    i = 0
    num_lines = len(lines)
    eq_counter = 0
    in_declarations = False

    while i < num_lines:
        line = lines[i]
        line_str = line.strip()

        # Empty line
        if not line_str:
            i += 1
            continue

        # Horizontal Rule
        if line_str in ("---", "***", "___"):
            hr_space = 3 if in_declarations else 6
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceBefore=hr_space, spaceAfter=hr_space))
            i += 1
            continue

        # Display Math: $$ ... $$
        if line_str.startswith("$$"):
            math_lines = []
            if line_str == "$$":
                i += 1
                while i < num_lines and not lines[i].strip().startswith("$$"):
                    math_lines.append(lines[i].strip())
                    i += 1
                i += 1
            else:
                m_inline = re.match(r"\$\$(.*?)\$\$", line_str)
                if m_inline:
                    math_lines.append(m_inline.group(1).strip())
                    i += 1
                else:
                    math_lines.append(line_str.replace("$$", "").strip())
                    i += 1
                    while i < num_lines and not lines[i].strip().startswith("$$"):
                        math_lines.append(lines[i].strip())
                        i += 1
                    i += 1
            raw_math = " ".join(math_lines)
            eq_counter += 1
            eq_flowable = render_equation_to_flowable(raw_math, eq_num=eq_counter, content_w=PORTRAIT_CONTENT_WIDTH)
            story.append(Spacer(1, 4))
            story.append(eq_flowable)
            story.append(Spacer(1, 4))
            continue

        # Figure Callouts: *[Figure X about here: ...]*
        fig_match = re.search(r"\*\[Figure (\d+) about here:.*?\]\*", line_str, re.IGNORECASE)
        if fig_match:
            fig_num = int(fig_match.group(1))
            fig_path = FIGURE_MAP.get(fig_num)
            if fig_path and os.path.exists(fig_path):
                pil_im = PILImage.open(fig_path)
                w_px, h_px = pil_im.size
                aspect = w_px / h_px

                max_w = PORTRAIT_CONTENT_WIDTH - 20
                target_w = max_w
                target_h = target_w / aspect
                
                if target_h > 420:
                    target_h = 420
                    target_w = target_h * aspect

                fig_img = Image(fig_path, width=target_w, height=target_h)
                fig_img.hAlign = "CENTER"

                fig_title, fig_cap = fig_captions.get(fig_num, (f"Figure {fig_num}", ""))
                formatted_cap = format_markdown_text(fig_cap)
                
                caption_flowables = [
                    Paragraph(f"<b>Figure {fig_num}: {fig_title}</b>", fig_title_style),
                    Paragraph(formatted_cap, fig_cap_style),
                ]

                fig_table = Table([[fig_img], [caption_flowables]], colWidths=[PORTRAIT_CONTENT_WIDTH])
                fig_table.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, 0), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                    ("TOPPADDING", (0, 1), (-1, 1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
                    ("LEFTPADDING", (0, 1), (-1, 1), 8),
                    ("RIGHTPADDING", (0, 1), (-1, 1), 8),
                ]))
                story.append(Spacer(1, 6))
                story.append(fig_table)
                story.append(Spacer(1, 6))
            else:
                print(f"Warning: Figure {fig_num} path not found: {fig_path}")
            i += 1
            continue

        # Table Headings: #### Table X: ...
        table_h_match = re.match(r"#### Table (\d+):([^\n]+)", line_str)
        if table_h_match:
            tab_num = int(table_h_match.group(1))
            tab_title = f"Table {tab_num}:{table_h_match.group(2)}"
            
            # =================================================================
            # TASK 2: TABLE 2 LANDSCAPE DEDICATED PRESENTATION
            # =================================================================
            if tab_num == 2:
                # Switch to Landscape Template
                story.append(NextPageTemplate("Landscape"))
                story.append(PageBreak())

                # Title and Notes in Landscape
                t2_title_land = ParagraphStyle("T2TitleLand", fontName=FONT_BOLD, fontSize=11, leading=14, textColor=colors.HexColor("#1e3a8a"), spaceAfter=4)
                t2_note_land = ParagraphStyle("T2NoteLand", fontName=FONT_ITALIC, fontSize=8.0, leading=11, textColor=colors.HexColor("#475569"), spaceAfter=5)

                story.append(Spacer(1, 10))
                story.append(Paragraph(format_markdown_text(tab_title), t2_title_land))
                i += 1

                # Collect notes before table
                while i < num_lines and (lines[i].strip().startswith("*") and not lines[i].strip().startswith("|")):
                    story.append(Paragraph(format_markdown_text(lines[i].strip()), t2_note_land))
                    i += 1

                # Skip to pipe table
                while i < num_lines and not lines[i].strip().startswith("|"):
                    i += 1

                # Collect pipe lines
                table_lines = []
                while i < num_lines and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1

                raw_headers = split_markdown_table_row(table_lines[0])
                raw_data_rows = []
                for r_line in table_lines[2:]:
                    if r_line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", r_line):
                        raw_data_rows.append(split_markdown_table_row(r_line))

                # Landscape Table 2 column widths totaling 770 pt (matches full landscape margin width)
                col_w_t2 = [48, 118, 80, 92, 80, 48, 76, 76, 76, 76]
                t2_flowable_rows = []

                # Headers
                h_cells = []
                for h_idx, h_text in enumerate(raw_headers):
                    align = TA_LEFT if h_idx < 2 else TA_CENTER
                    f_text = format_markdown_text(h_text)
                    h_cells.append(Paragraph(f"<b><font size='8.2' color='#ffffff'>{f_text}</font></b>", ParagraphStyle(f"T2H_{h_idx}", fontName=FONT_BOLD, alignment=align, leading=10.8)))
                t2_flowable_rows.append(h_cells)

                # Data rows
                for r_idx, r_cells in enumerate(raw_data_rows):
                    row_paras = []
                    for c_idx, c_text in enumerate(r_cells):
                        align = TA_LEFT if c_idx < 2 else TA_CENTER
                        f_text = format_markdown_text(c_text)
                        row_paras.append(Paragraph(f"<font size='8.0' color='#0f172a'>{f_text}</font>", ParagraphStyle(f"T2C_{r_idx}_{c_idx}", fontName=FONT_FAMILY, alignment=align, leading=10.6)))
                    t2_flowable_rows.append(row_paras)

                t2_table = Table(t2_flowable_rows, colWidths=col_w_t2, repeatRows=1)
                t2_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8.0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8.0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4.0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4.0),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]))
                story.append(Spacer(1, 4))
                story.append(t2_table)
                story.append(Spacer(1, 12))

                # Return to Portrait Template for subsequent sections
                story.append(NextPageTemplate("Portrait"))
                story.append(PageBreak())
                continue

            # Standard Portrait Tables
            story.append(Paragraph(format_markdown_text(tab_title), table_title_style))
            i += 1
            
            # Collect notes / protocol lines before the actual table
            while i < num_lines and (lines[i].strip().startswith("*") and not lines[i].strip().startswith("|") and not lines[i].strip().startswith("```")):
                note_str = lines[i].strip()
                story.append(Paragraph(format_markdown_text(note_str), table_note_style))
                i += 1
            
            # Table 6 (ASCII matrix) or regular pipe tables
            if tab_num == 6:
                while i < num_lines and not lines[i].strip().startswith("```"):
                    if lines[i].strip():
                        story.append(Paragraph(format_markdown_text(lines[i].strip()), table_note_style))
                    i += 1
                i += 1 # skip opening ```
                ascii_lines = []
                while i < num_lines and not lines[i].strip().startswith("```"):
                    ascii_lines.append(lines[i].strip())
                    i += 1
                i += 1 # skip closing ```

                t6_headers = ["Protocol Identifier", "Sample Unit", "Sample Count", "Decision Cutoff", "Metrics (Recall / Specificity / F1)"]
                t6_data = [
                    ["Protocol 1: Standard 0.50", "Outer Fold", "25 folds", "Fixed τ = 0.50", "Sens: 0.312 ± 0.086, Spec: 0.864 ± 0.074, F1: 0.403 ± 0.087"],
                    ["Protocol 2: Nested Tuned", "Outer Fold", "25 folds", "Inner-OOF dynamic", "Sens: 0.795 ± 0.109, Spec: 0.494 ± 0.143, F1: 0.604 ± 0.052"],
                    ["Protocol 3: Fixed 0.35 (Fold)", "Outer Fold", "25 folds", "Fixed τ = 0.35", "Sens: 0.742 ± 0.106, Spec: 0.575 ± 0.071, F1: 0.605 ± 0.068"],
                    ["Protocol 4: Fixed 0.35 (Repeat)", "CV Repeat", "5 repeats", "Fixed τ = 0.35", "Sens: 0.742 ± 0.025, Spec: 0.575 ± 0.011, F1: 0.606 ± 0.012"],
                ]
                col_w = [115, 65, 65, 95, 175]
                t_cells = []
                h_row = [Paragraph(f"<b><font size='7' color='#ffffff'>{h}</font></b>", ParagraphStyle("T6H", fontName=FONT_BOLD, alignment=TA_CENTER)) for h in t6_headers]
                t_cells.append(h_row)
                for r in t6_data:
                    row_cells = []
                    for c_idx, c_val in enumerate(r):
                        align = TA_LEFT if c_idx == 0 or c_idx == 4 else TA_CENTER
                        row_cells.append(Paragraph(f"<font size='7' color='#1e293b'>{c_val}</font>", ParagraphStyle("T6C", fontName=FONT_FAMILY, alignment=align)))
                    t_cells.append(row_cells)

                t_table = Table(t_cells, colWidths=col_w, repeatRows=1)
                t_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]))
                story.append(t_table)
                story.append(Spacer(1, 4))
                continue
            else:
                # Regular pipe table
                while i < num_lines and not lines[i].strip().startswith("|"):
                    if lines[i].strip():
                        story.append(Paragraph(format_markdown_text(lines[i].strip()), table_note_style))
                    i += 1
                
                table_lines = []
                while i < num_lines and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                
                if len(table_lines) >= 3:
                    raw_headers = split_markdown_table_row(table_lines[0])
                    num_cols = len(raw_headers)
                    raw_data_rows = []
                    for r_line in table_lines[2:]:
                        if r_line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", r_line):
                            raw_data_rows.append(split_markdown_table_row(r_line))

                    if tab_num == 1:
                        col_w = [140, 95, 95, 95, 88]
                        f_size, f_lead = 7.0, 9.0
                    elif tab_num == 3:
                        col_w = [45, 85, 75, 75, 75, 80, 75]
                        f_size, f_lead = 6.8, 8.5
                    elif tab_num == 4:
                        col_w = [40, 80, 65, 65, 65, 65, 65, 65]
                        f_size, f_lead = 6.6, 8.2
                    elif tab_num == 5:
                        col_w = [38, 70, 80, 55, 55, 55, 55, 55, 55]
                        f_size, f_lead = 6.4, 8.0
                    elif tab_num == 7:
                        col_w = [130, 95, 95, 95, 98]
                        f_size, f_lead = 7.0, 9.0
                    elif tab_num == 8:
                        col_w = [150, 90, 90, 90, 93]
                        f_size, f_lead = 7.0, 9.0
                    elif tab_num == 9:
                        col_w = [45, 80, 65, 65, 65, 65, 65, 60]
                        f_size, f_lead = 6.6, 8.2
                    elif tab_num == 10:
                        col_w = [40, 55, 55, 55, 55, 55, 55, 70, 70]
                        f_size, f_lead = 6.4, 8.0
                    elif tab_num == 11:
                        col_w = [90, 100, 55, 55, 55, 55, 103]
                        f_size, f_lead = 6.8, 8.5
                    elif tab_num == 12:
                        col_w = [55, 60, 35, 35, 35, 50, 50, 50, 50, 93]
                        f_size, f_lead = 6.2, 7.8
                    else:
                        col_w = [PORTRAIT_CONTENT_WIDTH / num_cols] * num_cols
                        f_size, f_lead = 6.8, 8.5

                    t_flowable_rows = []
                    
                    h_cells = []
                    for h_idx, h_text in enumerate(raw_headers):
                        align = TA_LEFT if h_idx == 0 else TA_CENTER
                        f_text = format_markdown_text(h_text)
                        h_para = Paragraph(f"<b><font size='{f_size}' color='#ffffff'>{f_text}</font></b>", ParagraphStyle(f"TH_{tab_num}_{h_idx}", fontName=FONT_BOLD, alignment=align, leading=f_lead))
                        h_cells.append(h_para)
                    t_flowable_rows.append(h_cells)

                    for r_idx, r_cells in enumerate(raw_data_rows):
                        row_paras = []
                        for c_idx, c_text in enumerate(r_cells):
                            align = TA_LEFT if c_idx == 0 or (tab_num == 11 and c_idx == 1) or (tab_num == 12 and c_idx == 9) else TA_CENTER
                            f_text = format_markdown_text(c_text)
                            c_para = Paragraph(f"<font size='{f_size}' color='#0f172a'>{f_text}</font>", ParagraphStyle(f"TC_{tab_num}_{r_idx}_{c_idx}", fontName=FONT_FAMILY, alignment=align, leading=f_lead))
                            row_paras.append(c_para)
                        t_flowable_rows.append(row_paras)

                    p_table = Table(t_flowable_rows, colWidths=col_w, repeatRows=1)
                    p_table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3.0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3.0),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ]))
                    story.append(p_table)
                    story.append(Spacer(1, 4))
                continue

        # Section Headings H1 to H4
        if line_str.startswith("##### "):
            story.append(Paragraph(format_markdown_text(line_str[6:].strip()), h4_style))
            i += 1
            continue
        if line_str.startswith("#### "):
            story.append(Paragraph(format_markdown_text(line_str[5:].strip()), h3_style))
            i += 1
            continue
        if line_str.startswith("### "):
            curr_h2 = dec_h2_style if in_declarations else h2_style
            story.append(Paragraph(format_markdown_text(line_str[4:].strip()), curr_h2))
            i += 1
            continue
        if line_str.startswith("## "):
            sec_title = line_str[3:].strip()
            if sec_title.startswith("Declarations"):
                in_declarations = True
            elif sec_title.startswith("References"):
                in_declarations = False
            # Start References cleanly on a dedicated page
            if sec_title.startswith("References"):
                story.append(PageBreak())
            story.append(Paragraph(format_markdown_text(sec_title), h1_style))
            i += 1
            continue

        # Blockquotes: > ...
        if line_str.startswith(">"):
            bq_lines = []
            while i < num_lines and lines[i].strip().startswith(">"):
                clean_bq = lines[i].strip().lstrip(">").strip()
                bq_lines.append(clean_bq)
                i += 1
            full_bq = " ".join(bq_lines)
            is_warning = "[!WARNING]" in full_bq or "[!CAUTION]" in full_bq or "AUTHOR CONFIRMATION" in full_bq
            accent_color = colors.HexColor("#d97706") if is_warning else colors.HexColor("#2563eb")
            bg_color = colors.HexColor("#fffbeb") if is_warning else colors.HexColor("#eff6ff")
            
            bq_para = Paragraph(format_markdown_text(full_bq), callout_style)
            bq_table = Table([[bq_para]], colWidths=[PORTRAIT_CONTENT_WIDTH])
            bq_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("LINELEFT", (0, 0), (0, 0), 3.0, accent_color),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(Spacer(1, 3))
            story.append(bq_table)
            story.append(Spacer(1, 3))
            continue

        # Bullet List Items: - ... or * ... (not bold or table headings)
        if (line_str.startswith("- ") or line_str.startswith("* ")) and not line_str.startswith("**Table"):
            b_text = line_str[2:].strip()
            while i + 1 < num_lines and lines[i+1].startswith("  ") and not lines[i+1].strip().startswith("- ") and not lines[i+1].strip().startswith("* "):
                i += 1
                b_text += " " + lines[i].strip()
            bullet_html = f"&bull;&nbsp;&nbsp;{format_markdown_text(b_text)}"
            curr_b_style = dec_bullet_style if in_declarations else bullet_style
            story.append(Paragraph(bullet_html, curr_b_style))
            i += 1
            continue

        # Numbered List Items: 1. ...
        num_list_match = re.match(r"^(\d+)\.\s+(.+)$", line_str)
        if num_list_match:
            n_num = num_list_match.group(1)
            n_text = num_list_match.group(2).strip()
            while i + 1 < num_lines and lines[i+1].startswith("   ") and not re.match(r"^\d+\.\s+", lines[i+1].strip()):
                i += 1
                n_text += " " + lines[i].strip()
            
            # Check if within References section
            if "## References" in body_markdown[:intro_start + md_text[intro_start:].find(line_str)]:
                ref_html = f"<b>[{n_num}]</b>&nbsp;&nbsp;{format_markdown_text(n_text)}"
                story.append(Paragraph(ref_html, ref_style))
            else:
                num_html = f"<b>{n_num}.</b>&nbsp;&nbsp;{format_markdown_text(n_text)}"
                story.append(Paragraph(num_html, numbered_style))
            i += 1
            continue

        # Normal Paragraph Prose
        p_lines = [line_str]
        while i + 1 < num_lines:
            next_l = lines[i+1].strip()
            if not next_l or next_l.startswith("#") or next_l.startswith("- ") or next_l.startswith("* ") or next_l.startswith("|") or next_l.startswith(">") or next_l.startswith("$$") or next_l.startswith("```") or next_l in ("---", "***", "___") or re.match(r"^\d+\.\s+", next_l) or "*[Figure" in next_l:
                break
            p_lines.append(next_l)
            i += 1
        full_p = " ".join(p_lines)
        curr_p_style = dec_body_style if in_declarations else body_style
        story.append(Paragraph(format_markdown_text(full_p), curr_p_style))
        i += 1

    print(f"Total flowables constructed: {len(story)}")
    print(f"Building PDF to: {PDF_OUT_MANUSCRIPT}")
    
    # Setup document templates with Portrait and Landscape PageTemplates
    frame_port = Frame(LEFT_MARGIN, BOTTOM_MARGIN, PORTRAIT_CONTENT_WIDTH, PORTRAIT_CONTENT_HEIGHT, id="FramePort")
    frame_land = Frame(LEFT_MARGIN, BOTTOM_MARGIN, LANDSCAPE_CONTENT_WIDTH, LANDSCAPE_CONTENT_HEIGHT, id="FrameLand")

    template_port = PageTemplate(id="Portrait", frames=frame_port, pagesize=A4)
    template_land = PageTemplate(id="Landscape", frames=frame_land, pagesize=landscape(A4))

    doc = BaseDocTemplate(
        PDF_OUT_MANUSCRIPT,
        pageTemplates=[template_port, template_land],
    )

    doc.build(story, canvasmaker=DynamicNumberedCanvas)
    print("PDF build completed successfully.")

    # Copy to root directory as well
    shutil.copy2(PDF_OUT_MANUSCRIPT, PDF_OUT_ROOT)
    print(f"Copied manuscript PDF to root: {PDF_OUT_ROOT}")

    # Inspect with pypdfium2
    pdf = pdfium.PdfDocument(PDF_OUT_MANUSCRIPT)
    num_pages = len(pdf)
    print(f"\n==========================================")
    print(f"SUCCESS: Generated {num_pages}-page PDF manuscript!")
    print(f"File 1: {PDF_OUT_MANUSCRIPT} ({os.path.getsize(PDF_OUT_MANUSCRIPT) / 1024:.1f} KB)")
    print(f"File 2: {PDF_OUT_ROOT} ({os.path.getsize(PDF_OUT_ROOT) / 1024:.1f} KB)")
    print(f"==========================================")

    return num_pages


if __name__ == "__main__":
    build_pdf()
