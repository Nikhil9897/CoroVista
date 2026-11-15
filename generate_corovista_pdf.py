#!/usr/bin/env python3
"""
CoroVista Technical Documentation — Redesigned PDF Generator (v3 - Clean Cover & Internal Pages)
Project: CoroVista — Cardiovascular Risk Visualization & Vessel-Specific Stenosis Prediction System
Team: Parallel Minds (Naman Deep Tripathi & Nikhil Agrawal)
"""

import os
import math
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, PageBreak
)
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, PolyLine, Polygon
)

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pt
MARGIN_X = 42
MARGIN_TOP = 48
MARGIN_BOTTOM = 42
CONTENT_W = PAGE_W - (2 * MARGIN_X)  # 511.27 pt

# Palette: Deep Navy, Slate, Restrained Clinical Teal & Sky Blue
NAVY_DARK = colors.HexColor("#0A1628")
NAVY_PRIMARY = colors.HexColor("#0F253E")
NAVY_MID = colors.HexColor("#1E3A5F")
TEAL_ACCENT = colors.HexColor("#0D9488")
TEAL_BG = colors.HexColor("#F0FDFA")
CYAN_GLOW = colors.HexColor("#38BDF8")
SLATE_TEXT = colors.HexColor("#1E293B")
SLATE_MUTED = colors.HexColor("#475569")
SLATE_LIGHT = colors.HexColor("#F8FAFC")
SLATE_BORDER = colors.HexColor("#CBD5E1")
AMBER_WARN = colors.HexColor("#D97706")
AMBER_BG = colors.HexColor("#FFFBEB")
AMBER_BORDER = colors.HexColor("#FCD34D")
CODE_BG = colors.HexColor("#0F172A")
WHITE = colors.white


def draw_cover_page(canvas, doc):
    """Draws a clean, uncrowded Healthcare-AI research report cover on Page 1."""
    canvas.saveState()

    # 1. Deep Navy Hero Section (Top 54% of Page — spacious & uncluttered)
    hero_h = 455
    hero_y = PAGE_H - hero_h
    canvas.setFillColor(NAVY_DARK)
    canvas.rect(0, hero_y, PAGE_W, hero_h, stroke=0, fill=1)

    # Subtle angled navy accent on the right half
    canvas.setFillColor(NAVY_PRIMARY)
    p = canvas.beginPath()
    p.moveTo(PAGE_W * 0.52, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H)
    p.lineTo(PAGE_W, hero_y)
    p.lineTo(PAGE_W * 0.66, hero_y)
    p.close()
    canvas.drawPath(p, stroke=0, fill=1)

    # Top accent bar
    canvas.setFillColor(TEAL_ACCENT)
    canvas.rect(0, PAGE_H - 6, PAGE_W * 0.68, 6, stroke=0, fill=1)
    canvas.setFillColor(CYAN_GLOW)
    canvas.rect(PAGE_W * 0.68, PAGE_H - 6, PAGE_W * 0.32, 6, stroke=0, fill=1)

    # Bottom teal border along the hero split
    canvas.setFillColor(TEAL_ACCENT)
    canvas.rect(0, hero_y - 3, PAGE_W, 3, stroke=0, fill=1)

    # 2. Left Hero Typography (Strong Focal Hierarchy + Deliberate Whitespace)
    # Document Type Pill Badge
    canvas.setFillColor(colors.HexColor("#112E4A"))
    canvas.setStrokeColor(TEAL_ACCENT)
    canvas.setLineWidth(1)
    canvas.roundRect(MARGIN_X, PAGE_H - 96, 202, 22, 4, stroke=1, fill=1)
    canvas.setFillColor(colors.HexColor("#5EEAD4"))
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(MARGIN_X + 11, PAGE_H - 88, "TECHNICAL PROJECT DOCUMENTATION")

    # Main Project Title
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 44)
    canvas.drawString(MARGIN_X, PAGE_H - 160, "CoroVista")

    # Teal Accent Rule
    canvas.setFillColor(TEAL_ACCENT)
    canvas.rect(MARGIN_X, PAGE_H - 178, 68, 3.5, stroke=0, fill=1)
    canvas.setFillColor(CYAN_GLOW)
    canvas.rect(MARGIN_X + 73, PAGE_H - 178, 22, 3.5, stroke=0, fill=1)

    # Project Subtitle
    canvas.setFillColor(colors.HexColor("#F1F5F9"))
    canvas.setFont("Helvetica-Bold", 15.5)
    canvas.drawString(MARGIN_X, PAGE_H - 210, "Cardiovascular Risk Visualization &")
    canvas.drawString(MARGIN_X, PAGE_H - 232, "Vessel-Specific Stenosis Prediction System")

    # Concise Lead Statement
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.setFont("Helvetica", 10.5)
    canvas.drawString(
        MARGIN_X, PAGE_H - 276,
        "A machine-learning workflow for cardiovascular risk assessment,"
    )
    canvas.drawString(
        MARGIN_X, PAGE_H - 293,
        "vessel-level prediction, and interpretable model outputs."
    )

    # 3. Right Hero Graphic: Tasteful Coronary Vessel Tree + AI Nodes
    cx, cy = 448, PAGE_H - 228
    canvas.setStrokeColor(colors.HexColor("#1E3A5F"))
    canvas.setLineWidth(1)
    canvas.circle(cx, cy, 92, stroke=1, fill=0)
    canvas.setStrokeColor(colors.HexColor("#164E63"))
    canvas.setDash(4, 4)
    canvas.circle(cx, cy, 70, stroke=1, fill=0)
    canvas.setDash()

    # Coronary Vessel Branches
    canvas.setLineCap(1)
    canvas.setStrokeColor(CYAN_GLOW)
    canvas.setLineWidth(3.0)
    vessel_lad = canvas.beginPath()
    vessel_lad.moveTo(cx - 5, cy + 62)
    vessel_lad.curveTo(cx - 10, cy + 36, cx - 26, cy + 12, cx - 33, cy - 15)
    vessel_lad.curveTo(cx - 38, cy - 35, cx - 24, cy - 52, cx - 16, cy - 66)
    canvas.drawPath(vessel_lad, stroke=1, fill=0)

    canvas.setStrokeColor(TEAL_ACCENT)
    canvas.setLineWidth(2.5)
    vessel_lcx = canvas.beginPath()
    vessel_lcx.moveTo(cx - 17, cy + 28)
    vessel_lcx.curveTo(cx - 42, cy + 15, cx - 60, cy - 5, cx - 54, cy - 34)
    canvas.drawPath(vessel_lcx, stroke=1, fill=0)

    canvas.setStrokeColor(colors.HexColor("#2DD4BF"))
    canvas.setLineWidth(2.6)
    vessel_rca = canvas.beginPath()
    vessel_rca.moveTo(cx + 8, cy + 52)
    vessel_rca.curveTo(cx + 40, cy + 30, cx + 52, cy - 5, cx + 30, cy - 48)
    canvas.drawPath(vessel_rca, stroke=1, fill=0)

    canvas.setLineWidth(1.4)
    canvas.line(cx - 30, cy - 2, cx - 10, cy - 22)
    canvas.line(cx + 38, cy + 10, cx + 56, cy - 12)

    nodes = [
        (cx - 5, cy + 62, "Cath", CYAN_GLOW),
        (cx - 33, cy - 15, "LAD", colors.HexColor("#F43F5E")),
        (cx - 54, cy - 18, "LCX", TEAL_ACCENT),
        (cx + 42, cy + 8, "RCA", colors.HexColor("#38BDF8")),
    ]
    for nx, ny, label, ncolor in nodes:
        canvas.setFillColor(NAVY_DARK)
        canvas.setStrokeColor(ncolor)
        canvas.setLineWidth(2)
        canvas.circle(nx, ny, 5, stroke=1, fill=1)
        canvas.setFillColor(ncolor)
        canvas.circle(nx, ny, 2.2, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#E2E8F0"))
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawString(nx + 8, ny - 2.5, label)

    # Subtle ECG Waveform at base of circle
    canvas.setStrokeColor(TEAL_ACCENT)
    canvas.setLineWidth(1.3)
    ecg = canvas.beginPath()
    bx, by = cx - 78, cy - 82
    ecg.moveTo(bx, by)
    ecg.lineTo(bx + 32, by)
    ecg.lineTo(bx + 38, by + 5)
    ecg.lineTo(bx + 44, by - 4)
    ecg.lineTo(bx + 50, by + 19)
    ecg.lineTo(bx + 56, by - 12)
    ecg.lineTo(bx + 62, by + 7)
    ecg.lineTo(bx + 68, by)
    ecg.lineTo(bx + 156, by)
    canvas.drawPath(ecg, stroke=1, fill=0)

    # 4. Lower White Canvas: Clean, Uncrowded Team & Author Presentation
    team_top = hero_y - 68

    # Vertical Accent Bar next to Team Block
    canvas.setFillColor(TEAL_ACCENT)
    canvas.rect(MARGIN_X, team_top - 96, 4, 96, stroke=0, fill=1)

    canvas.setFillColor(TEAL_ACCENT)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(MARGIN_X + 18, team_top - 12, "PROJECT TEAM")

    canvas.setFillColor(NAVY_DARK)
    canvas.setFont("Helvetica-Bold", 20)
    canvas.drawString(MARGIN_X + 18, team_top - 38, "Team Parallel Minds")

    canvas.setFillColor(SLATE_MUTED)
    canvas.setFont("Helvetica-Bold", 8.2)
    canvas.drawString(MARGIN_X + 18, team_top - 64, "TEAM MEMBERS")

    # Two clean member cards side-by-side
    member_y = team_top - 100
    card_w = 195
    card_h = 28
    members = ["Naman Deep Tripathi", "Nikhil Agrawal"]
    for idx, m_name in enumerate(members):
        mx = MARGIN_X + 18 + idx * (card_w + 16)
        canvas.setFillColor(SLATE_LIGHT)
        canvas.setStrokeColor(SLATE_BORDER)
        canvas.setLineWidth(0.9)
        canvas.roundRect(mx, member_y, card_w, card_h, 4, stroke=1, fill=1)
        canvas.setFillColor(TEAL_ACCENT)
        canvas.circle(mx + 14, member_y + 14, 3, stroke=0, fill=1)
        canvas.setFillColor(NAVY_DARK)
        canvas.setFont("Helvetica-Bold", 10.5)
        canvas.drawString(mx + 25, member_y + 10, m_name)

    # 5. Subtle Provenance Note above Footer (No bulky yellow warning box on Cover)
    note_y = 66
    canvas.setFillColor(SLATE_LIGHT)
    canvas.setStrokeColor(SLATE_BORDER)
    canvas.setLineWidth(0.75)
    canvas.roundRect(MARGIN_X, note_y, CONTENT_W, 42, 4, stroke=1, fill=1)

    canvas.setFillColor(SLATE_MUTED)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(MARGIN_X + 14, note_y + 25, "DOCUMENTATION NOTE")
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(
        MARGIN_X + 14, note_y + 11,
        "Prepared from repository documentation. Performance metrics are identified as repository-reported, not independently validated."
    )

    # Cover Footer
    canvas.setStrokeColor(SLATE_BORDER)
    canvas.setLineWidth(0.75)
    canvas.line(MARGIN_X, 42, PAGE_W - MARGIN_X, 42)
    canvas.setFillColor(SLATE_MUTED)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(MARGIN_X, 28, "COROVISTA  •  TECHNICAL DOCUMENTATION")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(PAGE_W - MARGIN_X, 28, "Page 1 of 4")

    canvas.restoreState()


def draw_internal_page(canvas, doc):
    """Draws clean headers and footers on Pages 2–4 WITHOUT repeating Team/Member names."""
    canvas.saveState()

    # Running Header (Strictly Project Title & Document Type — No Team/Author Names)
    header_y = PAGE_H - 30
    canvas.setFillColor(NAVY_PRIMARY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(MARGIN_X, header_y, "COROVISTA")
    canvas.setFillColor(TEAL_ACCENT)
    canvas.drawString(MARGIN_X + 54, header_y, "•")
    canvas.setFillColor(SLATE_MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        MARGIN_X + 64, header_y,
        "Cardiovascular Risk Visualization & Vessel-Specific Stenosis Prediction System"
    )

    # Header Rule with Teal Accent
    canvas.setStrokeColor(SLATE_BORDER)
    canvas.setLineWidth(0.75)
    canvas.line(MARGIN_X, header_y - 6, PAGE_W - MARGIN_X, header_y - 6)
    canvas.setStrokeColor(TEAL_ACCENT)
    canvas.setLineWidth(2)
    canvas.line(MARGIN_X, header_y - 6, MARGIN_X + 48, header_y - 6)

    # Running Footer (Strictly Document Label & Page Number — No Team/Author Names)
    footer_y = 24
    canvas.setStrokeColor(SLATE_BORDER)
    canvas.setLineWidth(0.75)
    canvas.line(MARGIN_X, footer_y + 12, PAGE_W - MARGIN_X, footer_y + 12)

    canvas.setFillColor(SLATE_MUTED)
    canvas.setFont("Helvetica-Bold", 7.8)
    canvas.drawString(MARGIN_X, footer_y, "COROVISTA  TECHNICAL DOCUMENTATION")
    canvas.setFillColor(NAVY_PRIMARY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(PAGE_W - MARGIN_X, footer_y, f"Page {doc.page} of 4")

    canvas.restoreState()


def build_styles():
    """Creates standardized typography styles."""
    base = getSampleStyleSheet()
    styles = {}

    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13.0,
        textColor=SLATE_TEXT,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    styles["BodySmall"] = ParagraphStyle(
        "BodySmall",
        parent=styles["Body"],
        fontSize=8.4,
        leading=11.8,
        textColor=SLATE_MUTED,
        spaceAfter=3,
    )
    styles["SubHeading"] = ParagraphStyle(
        "SubHeading",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.0,
        leading=13.5,
        textColor=NAVY_PRIMARY,
        spaceBefore=5,
        spaceAfter=3.5,
    )
    styles["Bullet"] = ParagraphStyle(
        "Bullet",
        parent=styles["Body"],
        fontSize=8.9,
        leading=12.2,
        leftIndent=11,
        firstLineIndent=-11,
        spaceAfter=3,
    )
    styles["TableHeader"] = ParagraphStyle(
        "TableHeader",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.4,
        leading=10.8,
        textColor=WHITE,
    )
    styles["TableHeaderCenter"] = ParagraphStyle(
        "TableHeaderCenter",
        parent=styles["TableHeader"],
        alignment=TA_CENTER,
    )
    styles["TableCell"] = ParagraphStyle(
        "TableCell",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=SLATE_TEXT,
    )
    styles["TableCellBold"] = ParagraphStyle(
        "TableCellBold",
        parent=styles["TableCell"],
        fontName="Helvetica-Bold",
        textColor=NAVY_PRIMARY,
    )
    styles["TableCellCenter"] = ParagraphStyle(
        "TableCellCenter",
        parent=styles["TableCell"],
        alignment=TA_CENTER,
    )
    styles["TableCellMono"] = ParagraphStyle(
        "TableCellMono",
        parent=styles["TableCell"],
        fontName="Courier-Bold",
        fontSize=8.2,
        textColor=colors.HexColor("#0F766E"),
    )
    styles["Caption"] = ParagraphStyle(
        "Caption",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.1,
        leading=10.8,
        textColor=SLATE_MUTED,
        alignment=TA_CENTER,
        spaceBefore=2.5,
        spaceAfter=5,
    )
    styles["CodeBlock"] = ParagraphStyle(
        "CodeBlock",
        parent=base["Normal"],
        fontName="Courier",
        fontSize=7.9,
        leading=11.4,
        textColor=colors.HexColor("#E2E8F0"),
    )
    return styles


def make_section_header(num_str, title_str):
    """Builds a polished section banner with a numbered pill badge and bottom rule."""
    num_p = Paragraph(
        f'<font name="Helvetica-Bold" size="9.5" color="#FFFFFF">{num_str}</font>',
        ParagraphStyle("SecNum", alignment=TA_CENTER, leading=11)
    )
    title_p = Paragraph(
        f'<font name="Helvetica-Bold" size="13" color="#0F253E">{title_str}</font>',
        ParagraphStyle("SecTitle", alignment=TA_LEFT, leading=15)
    )
    t = Table([[num_p, title_p]], colWidths=[26, CONTENT_W - 26], rowHeights=[21])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), TEAL_ACCENT),
        ("BACKGROUND", (1, 0), (1, 0), SLATE_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, NAVY_PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def draw_arrow(d, x1, y1, x2, y2, color=NAVY_MID):
    """Draws a crisp line with a filled triangular arrowhead at (x2, y2)."""
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.5))
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 5.2
    p1x = x2 - size * math.cos(angle - math.pi / 6)
    p1y = y2 - size * math.sin(angle - math.pi / 6)
    p2x = x2 - size * math.cos(angle + math.pi / 6)
    p2y = y2 - size * math.sin(angle + math.pi / 6)
    d.add(Polygon([x2, y2, p1x, p1y, p2x, p2y], fillColor=color, strokeColor=color))


def build_architecture_flowchart():
    """Creates Figure 1: Native vector system architecture flowchart."""
    w, h = CONTENT_W, 160
    d = Drawing(w, h)

    d.add(Rect(0, 0, w, h, rx=6, ry=6, fillColor=colors.HexColor("#F8FAFC"),
               strokeColor=SLATE_BORDER, strokeWidth=0.9))

    box_w, box_h = 136, 44
    gap_x = (w - 40 - 3 * box_w) / 2
    x1 = 20
    x2 = x1 + box_w + gap_x
    x3 = x2 + box_w + gap_x

    top_y = 103
    bot_y = 35

    def add_node(x, y, step_tag, title, sub1, sub2, border_col, fill_col, header_col):
        d.add(Rect(x, y, box_w, box_h, rx=5, ry=5, fillColor=fill_col,
                   strokeColor=border_col, strokeWidth=1.3))
        d.add(Rect(x, y + box_h - 5, box_w, 5, rx=2, ry=2, fillColor=header_col, strokeColor=None))
        d.add(String(x + 8, y + box_h - 15, step_tag, fontName="Helvetica-Bold",
                     fontSize=7, fillColor=header_col))
        d.add(String(x + box_w / 2, y + box_h - 16, title, fontName="Helvetica-Bold",
                     fontSize=9.0, fillColor=NAVY_DARK, textAnchor="middle"))
        d.add(String(x + box_w / 2, y + 15, sub1, fontName="Helvetica",
                     fontSize=7.6, fillColor=SLATE_MUTED, textAnchor="middle"))
        if sub2:
            d.add(String(x + box_w / 2, y + 5, sub2, fontName="Helvetica",
                         fontSize=7.6, fillColor=SLATE_MUTED, textAnchor="middle"))

    add_node(x1, top_y, "01", "User / Browser", "Structured clinical", "feature input",
             NAVY_MID, WHITE, NAVY_MID)
    add_node(x2, top_y, "02", "Frontend", "React / Vite UI", "Request & visualization",
             NAVY_MID, WHITE, NAVY_MID)
    add_node(x3, top_y, "03", "FastAPI Backend", "Schema validation", "& endpoint routing",
             TEAL_ACCENT, TEAL_BG, TEAL_ACCENT)

    add_node(x1, bot_y, "04", "Preprocessing", "Feature alignment", "Type / value checks",
             AMBER_WARN, AMBER_BG, AMBER_WARN)
    add_node(x2, bot_y, "05", "ML Models", "Cardiovascular risk &", "vessel stenosis predictions",
             NAVY_MID, WHITE, NAVY_MID)
    add_node(x3, bot_y, "06", "SHAP Explainability", "Feature attribution", "relative to reference",
             TEAL_ACCENT, TEAL_BG, TEAL_ACCENT)

    mid_top = top_y + box_h / 2
    draw_arrow(d, x1 + box_w, mid_top, x2, mid_top, NAVY_MID)
    draw_arrow(d, x2 + box_w, mid_top, x3, mid_top, NAVY_MID)

    mid_y_channel = (top_y + bot_y + box_h) / 2
    c3_x = x3 + box_w / 2
    c1_x = x1 + box_w / 2
    d.add(PolyLine([
        c3_x, top_y,
        c3_x, mid_y_channel,
        c1_x, mid_y_channel,
    ], strokeColor=NAVY_MID, strokeWidth=1.5))
    draw_arrow(d, c1_x, mid_y_channel, c1_x, bot_y + box_h, NAVY_MID)

    mid_bot = bot_y + box_h / 2
    draw_arrow(d, x1 + box_w, mid_bot, x2, mid_bot, NAVY_MID)
    draw_arrow(d, x2 + box_w, mid_bot, x3, mid_bot, NAVY_MID)

    bus_y = 12
    d.add(Rect(x1, bus_y - 5, w - 40, 17, rx=4, ry=4,
               fillColor=NAVY_PRIMARY, strokeColor=None))
    d.add(String(w / 2, bus_y,
                 "Response to interface:  predictions  •  risk scores  •  SHAP explanations",
                 fontName="Helvetica-Bold", fontSize=8.1, fillColor=WHITE, textAnchor="middle"))

    c2_x = x2 + box_w / 2
    draw_arrow(d, c2_x, bot_y, c2_x, bus_y + 12, TEAL_ACCENT)
    draw_arrow(d, c3_x, bot_y, c3_x, bus_y + 12, TEAL_ACCENT)

    return d


def styled_table(data, col_widths, styles, center_cols=(), pad_v=4.2):
    """Helper to apply consistent header, alternating row backgrounds, and padding."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), pad_v + 0.8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), pad_v + 0.8),
        ("TOPPADDING", (0, 1), (-1, -1), pad_v),
        ("BOTTOMPADDING", (0, 1), (-1, -1), pad_v),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, TEAL_ACCENT),
    ]
    for r in range(1, len(data)):
        bg = WHITE if r % 2 == 1 else SLATE_LIGHT
        cmds.append(("BACKGROUND", (0, r), (-1, r), bg))
    for c in center_cols:
        cmds.append(("ALIGN", (c, 0), (c, -1), "CENTER"))
    t.setStyle(TableStyle(cmds))
    return t


class DocAssignNextTemplate(Spacer):
    """Flowable that switches to a named PageTemplate on the following page."""
    def __init__(self, template_id):
        super().__init__(0, 0)
        self.template_id = template_id

    def wrap(self, availWidth, availHeight):
        self._doctemplate.handle_nextPageTemplate(self.template_id)
        return (0, 0)


def build_pdf(output_path="CoroVista_Technical_Documentation_Parallel_Minds_Redesigned.pdf"):
    styles = build_styles()

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="CoroVista — Technical Documentation",
        author="Team Parallel Minds (Naman Deep Tripathi, Nikhil Agrawal)",
        subject="Cardiovascular Risk Visualization & Vessel-Specific Stenosis Prediction System",
    )

    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="CoverFrame")
    internal_frame = Frame(
        MARGIN_X, MARGIN_BOTTOM, CONTENT_W, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="InternalFrame"
    )

    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover_page),
        PageTemplate(id="Internal", frames=[internal_frame], onPage=draw_internal_page),
    ])

    story = []

    # =========================================================================
    # PAGE 1: CLEAN COVER PAGE
    # =========================================================================
    story.append(DocAssignNextTemplate("Internal"))
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: SECTION 01 (PROJECT OVERVIEW) + SECTION 02 (SYSTEM ARCHITECTURE)
    # =========================================================================
    story.append(make_section_header("01", "Project Overview"))
    story.append(Spacer(1, 5))

    overview_left = [
        Paragraph(
            "<b>Abstract.</b> CoroVista is a machine-learning project focused on cardiovascular risk "
            "visualization and vessel-specific stenosis prediction. It combines a web interface, API "
            "backend, data preprocessing, trained prediction models, and SHAP-based feature attribution "
            "to make model outputs easier to inspect.",
            styles["Body"]
        ),
        Paragraph(
            "<b>Problem context.</b> A single overall score may not communicate how predicted risk "
            "differs across coronary vessels. CoroVista organizes outputs by target and presents "
            "feature-attribution information alongside predictions.",
            styles["Body"]
        ),
    ]
    overview_right = [
        Paragraph(
            "<b>Objective.</b> Accept structured clinical features, prepare them for inference, return "
            "predictions, and provide explanations that help users inspect which inputs contributed to a "
            "model output.",
            styles["Body"]
        ),
        Spacer(1, 2),
        Table(
            [[Paragraph(
                '<font name="Helvetica-Bold" color="#92400E">Scope note:</font> '
                '<font color="#78350F">CoroVista is a research/prototype system, not a validated '
                'clinical device. Do not use it as the sole basis for diagnosis or treatment.</font>',
                styles["BodySmall"]
            )]],
            colWidths=[CONTENT_W * 0.47 - 6],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), AMBER_BG),
                ("BOX", (0, 0), (-1, -1), 0.8, AMBER_BORDER),
                ("LINEBEFORE", (0, 0), (0, -1), 3, AMBER_WARN),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
    ]

    ov_grid = Table(
        [[overview_left, overview_right]],
        colWidths=[CONTENT_W * 0.53 - 6, CONTENT_W * 0.47 - 6]
    )
    ov_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(ov_grid)
    story.append(Spacer(1, 5))

    story.append(Paragraph("Document Map", styles["SubHeading"]))
    doc_map_data = [
        [
            Paragraph("Sec.", styles["TableHeaderCenter"]),
            Paragraph("Section Title", styles["TableHeader"]),
            Paragraph("Coverage", styles["TableHeader"]),
        ],
        [Paragraph("02", styles["TableCellCenter"]), Paragraph("System architecture", styles["TableCellBold"]), Paragraph("Flowchart and component responsibilities", styles["TableCell"])],
        [Paragraph("03", styles["TableCellCenter"]), Paragraph("Data and preprocessing", styles["TableCellBold"]), Paragraph("Dataset description and input preparation", styles["TableCell"])],
        [Paragraph("04", styles["TableCellCenter"]), Paragraph("Models and reported results", styles["TableCellBold"]), Paragraph("Model metrics and decision thresholds from project documentation", styles["TableCell"])],
        [Paragraph("05", styles["TableCellCenter"]), Paragraph("Explainability and API", styles["TableCellBold"]), Paragraph("SHAP feature attribution and REST endpoint overview", styles["TableCell"])],
        [Paragraph("06", styles["TableCellCenter"]), Paragraph("Local setup and testing", styles["TableCellBold"]), Paragraph("Development workflow, CLI commands, and verification checks", styles["TableCell"])],
        [Paragraph("07", styles["TableCellCenter"]), Paragraph("Limitations and references", styles["TableCellBold"]), Paragraph("Key limitations, responsible-use statement, and project sources", styles["TableCell"])],
    ]
    story.append(styled_table(doc_map_data, [36, 155, CONTENT_W - 191], styles, center_cols=(0,)))
    story.append(Spacer(1, 10))

    # SECTION 02: SYSTEM ARCHITECTURE
    story.append(make_section_header("02", "System Architecture"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "The diagram summarizes the request path: the frontend collects and presents information; the backend "
        "validates and routes requests; preprocessing aligns inputs with trained models; predictions and "
        "explainability outputs return to the interface.",
        styles["Body"]
    ))
    story.append(Spacer(1, 2))
    story.append(build_architecture_flowchart())
    story.append(Paragraph(
        "Figure 1. Conceptual application and inference flow based on repository structure and documented functionality.",
        styles["Caption"]
    ))

    story.append(Paragraph("Component Responsibilities", styles["SubHeading"]))
    comp_data = [
        [Paragraph("Component", styles["TableHeader"]), Paragraph("Responsibility", styles["TableHeader"])],
        [Paragraph("Frontend", styles["TableCellBold"]), Paragraph("Presents the React/Vite UI and sends structured API requests to the backend.", styles["TableCell"])],
        [Paragraph("FastAPI backend", styles["TableCellBold"]), Paragraph("Exposes health, model/feature metadata, prediction, explanation, and combined analysis routes.", styles["TableCell"])],
        [Paragraph("Preprocessing", styles["TableCellBold"]), Paragraph("Aligns input data with the feature order and representation expected by trained models.", styles["TableCell"])],
        [Paragraph("Prediction models", styles["TableCellBold"]), Paragraph("Generate overall cardiovascular risk or vessel-specific stenosis predictions.", styles["TableCell"])],
        [Paragraph("SHAP explainability", styles["TableCellBold"]), Paragraph("Provides feature-attribution information for individual model predictions.", styles["TableCell"])],
    ]
    story.append(styled_table(comp_data, [130, CONTENT_W - 130], styles))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: SECTION 03 (DATA & PREPROCESSING) + SECTION 04 (MODELS & RESULTS)
    # =========================================================================
    story.append(make_section_header("03", "Data and Preprocessing"))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The repository documentation identifies the <b>Extended Z-Alizadeh Sani</b> dataset as the principal "
        "dataset, with <b>303 records</b> and <b>54 features</b>. These figures are reproduced from project "
        "documentation and are not independently audited here.",
        styles["Body"]
    ))
    story.append(Paragraph(
        "Preprocessing matters because trained estimators expect features in a specific order and compatible "
        "data types. The project includes a pipeline to transform incoming records into model-ready inputs.",
        styles["Body"]
    ))

    story.append(Paragraph("Preprocessing Considerations", styles["SubHeading"]))
    prep_bullets = [
        ("Feature alignment:", "keep inference columns consistent with the exact features used during training."),
        ("Data types:", "represent numerical and categorical/string columns in formats accepted by the pipeline."),
        ("Missing or malformed values:", "validate requests and handle unsupported values rather than silently treating them as valid observations."),
        ("Inference consistency:", "apply the exact same transformations at prediction time as during training."),
    ]
    for b_title, b_text in prep_bullets:
        story.append(Paragraph(f'<font color="#0D9488">•</font>  <b>{b_title}</b> {b_text}', styles["Bullet"]))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Data Summary", styles["SubHeading"]))
    data_summary_rows = [
        [
            Paragraph("Item", styles["TableHeader"]),
            Paragraph("Documented Value", styles["TableHeader"]),
            Paragraph("Meaning", styles["TableHeader"]),
        ],
        [Paragraph("Dataset", styles["TableCellBold"]), Paragraph("Extended Z-Alizadeh Sani", styles["TableCell"]), Paragraph("Principal dataset named in project documentation", styles["TableCell"])],
        [Paragraph("Records", styles["TableCellBold"]), Paragraph("303", styles["TableCell"]), Paragraph("Reported dataset sample size", styles["TableCell"])],
        [Paragraph("Features", styles["TableCellBold"]), Paragraph("54", styles["TableCell"]), Paragraph("Reported input clinical feature count", styles["TableCell"])],
    ]
    story.append(styled_table(data_summary_rows, [110, 165, CONTENT_W - 275], styles, pad_v=4.8))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<i>Note:</i> Dataset composition and validation scope limit generalization; results should not be "
        "assumed to transfer to every population or clinical setting.",
        styles["BodySmall"]
    ))

    story.append(Spacer(1, 14))

    # SECTION 04: MODELS AND REPORTED RESULTS
    story.append(make_section_header("04", "Models and Reported Results"))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The repository reports <b>ROC-AUC</b> and <b>PR-AUC</b>. ROC-AUC summarizes ranking discrimination "
        "across thresholds; PR-AUC summarizes the precision–recall trade-off and can be particularly "
        "informative when class distributions are imbalanced.",
        styles["Body"]
    ))

    story.append(Paragraph("Repository-Reported Metrics & Decision Thresholds", styles["SubHeading"]))
    metrics_data = [
        [
            Paragraph("Target / Model", styles["TableHeader"]),
            Paragraph("ROC-AUC (Mean \u00b1 SD)", styles["TableHeaderCenter"]),
            Paragraph("PR-AUC (Mean \u00b1 SD)", styles["TableHeaderCenter"]),
            Paragraph("Recorded Threshold", styles["TableHeaderCenter"]),
        ],
        [
            Paragraph("Cath — XGBoost", styles["TableCellBold"]),
            Paragraph("0.915 \u00b1 0.041", styles["TableCellCenter"]),
            Paragraph("0.962 \u00b1 0.020", styles["TableCellCenter"]),
            Paragraph("0.50", styles["TableCellCenter"]),
        ],
        [
            Paragraph("LAD — Model reported in repo", styles["TableCellBold"]),
            Paragraph("0.842 \u00b1 0.048", styles["TableCellCenter"]),
            Paragraph("0.880 \u00b1 0.042", styles["TableCellCenter"]),
            Paragraph("0.50", styles["TableCellCenter"]),
        ],
        [
            Paragraph("LCX — Model reported in repo", styles["TableCellBold"]),
            Paragraph("0.738 \u00b1 0.061", styles["TableCellCenter"]),
            Paragraph("0.622 \u00b1 0.087", styles["TableCellCenter"]),
            Paragraph("0.50", styles["TableCellCenter"]),
        ],
        [
            Paragraph("RCA — Logistic Regression", styles["TableCellBold"]),
            Paragraph("0.716 \u00b1 0.057", styles["TableCellCenter"]),
            Paragraph("0.609 \u00b1 0.073", styles["TableCellCenter"]),
            Paragraph("0.38", styles["TableCellCenter"]),
        ],
    ]
    story.append(styled_table(metrics_data, [185, 115, 115, CONTENT_W - 415], styles, center_cols=(1, 2, 3), pad_v=4.8))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Thresholds recorded in project documentation: <b>Cath 0.50</b>; <b>LAD 0.50</b>; "
        "<b>LCX 0.50</b>; <b>RCA 0.38</b>.",
        styles["BodySmall"]
    ))

    story.append(Paragraph("Interpretation Notes", styles["SubHeading"]))
    interp_notes = [
        "The <b>\u00b1</b> values are reproduced as documented; their exact statistical meaning (e.g., cross-validation standard deviation vs. confidence interval) should be confirmed from experiment artifacts.",
        "These are <b>repository-reported results</b>, not independently reproduced benchmarks. Evaluation splits and external validation should be checked in experiment records.",
        "A high AUC alone does not establish clinical usefulness, probability calibration, patient safety, or cross-population generalization.",
    ]
    for note in interp_notes:
        story.append(Paragraph(f'<font color="#0D9488">•</font>  {note}', styles["Bullet"]))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: SECTIONS 05 (API), 06 (SETUP & TESTING), AND 07 (LIMITATIONS)
    # =========================================================================
    story.append(make_section_header("05", "Explainability and API Surface"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "CoroVista includes SHAP-based feature attribution. SHAP estimates how input features contribute to a "
        "model output relative to a reference/background distribution. These attributions describe model "
        "behavior; they do not establish clinical causation.",
        styles["Body"]
    ))

    api_rows = [
        [Paragraph("Endpoint", styles["TableHeader"]), Paragraph("Documented Purpose", styles["TableHeader"])],
        [Paragraph("/api/v1/health", styles["TableCellMono"]), Paragraph("Health/status check; reports whether models are loaded.", styles["TableCell"])],
        [Paragraph("/models", styles["TableCellMono"]), Paragraph("Model metadata or available model information.", styles["TableCell"])],
        [Paragraph("/features", styles["TableCellMono"]), Paragraph("Feature metadata used by the application.", styles["TableCell"])],
        [Paragraph("/predict", styles["TableCellMono"]), Paragraph("Prediction request endpoint.", styles["TableCell"])],
        [Paragraph("/explain", styles["TableCellMono"]), Paragraph("Explanation / feature-attribution request endpoint.", styles["TableCell"])],
        [Paragraph("/analyze", styles["TableCellMono"]), Paragraph("Combined analysis flow for predictions and explanations.", styles["TableCell"])],
    ]
    api_table = styled_table(api_rows, [84, 224], styles, pad_v=3.5)

    lifecycle_box = [
        Paragraph("Typical Request Lifecycle", styles["SubHeading"]),
        Paragraph('<font color="#0D9488">1.</font>  Client submits a structured feature payload.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">2.</font>  Backend validates the request and runs preprocessing.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">3.</font>  Selected model generates predictions; explainability path computes attributions when requested.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">4.</font>  Backend returns a structured response for the frontend to render.', styles["Bullet"]),
        Spacer(1, 2),
        Paragraph(
            "<i>Schema verification:</i> Confirm exact request schemas and response payloads against the "
            "running OpenAPI page (<code>/docs</code>), as API contracts can change.",
            styles["BodySmall"]
        ),
    ]

    sec5_grid = Table([[api_table, lifecycle_box]], colWidths=[316, CONTENT_W - 316])
    sec5_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(sec5_grid)
    story.append(Spacer(1, 7))

    # SECTION 06: LOCAL SETUP AND TESTING
    story.append(make_section_header("06", "Local Setup and Testing"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Local development used a Python virtual environment, FastAPI/Uvicorn backend, and Vite frontend. "
        "The backend uses port <b>8001</b> in this setup because another service occupied port 8000.",
        styles["Body"]
    ))

    code_lines = (
        '<font color="#38BDF8"># 1. Activate environment &amp; launch FastAPI backend</font><br/>'
        'cd ~/Projects/CoroVista<br/>'
        'source .venv/bin/activate<br/>'
        'uvicorn backend.app.main:app --host 127.0.0.1 --port 8001 --reload<br/><br/>'
        '<font color="#38BDF8"># 2. Launch React / Vite development server</font><br/>'
        'cd frontend<br/>'
        'npm run dev'
    )
    code_box = Table(
        [[Paragraph(code_lines, styles["CodeBlock"])]],
        colWidths=[246],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
            ("BOX", (0, 0), (-1, -1), 1, NAVY_MID),
            ("TOPPADDING", (0, 0), (-1, -1), 5.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    url_box = Table(
        [
            [Paragraph("Service", styles["TableHeader"]), Paragraph("Expected Local URL", styles["TableHeader"])],
            [Paragraph("Frontend UI", styles["TableCellBold"]), Paragraph("http://localhost:5173", styles["TableCellMono"])],
            [Paragraph("Backend API", styles["TableCellBold"]), Paragraph("http://127.0.0.1:8001", styles["TableCellMono"])],
            [Paragraph("OpenAPI Docs", styles["TableCellBold"]), Paragraph("http://127.0.0.1:8001/docs", styles["TableCellMono"])],
        ],
        colWidths=[82, 164]
    )
    url_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, SLATE_BORDER),
        ("BACKGROUND", (0, 1), (-1, 1), WHITE),
        ("BACKGROUND", (0, 2), (-1, 2), SLATE_LIGHT),
        ("BACKGROUND", (0, 3), (-1, 3), WHITE),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    setup_left = [
        Paragraph("Commands & Expected URLs", styles["SubHeading"]),
        code_box,
        Spacer(1, 4),
        url_box,
    ]

    setup_right = [
        Paragraph("Verification Checklist", styles["SubHeading"]),
        Paragraph('<font color="#0D9488">•</font>  Confirm the health endpoint responds and reports expected model-loading status.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  Ensure frontend API base URL points to port 8001 and CORS allows <code>localhost:5173</code> / <code>127.0.0.1:5173</code>.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  Run an analysis request and inspect predictions and explanation payloads.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  Check logs for model-loading errors, feature mismatches, or dependency incompatibilities.', styles["Bullet"]),
        Paragraph("Testing Notes", styles["SubHeading"]),
        Paragraph(
            "Earlier local integration notes recorded a successful health check and synthetic analysis "
            "response with <b>HTTP 200</b>, including prediction and SHAP outputs. A prior run reported "
            "<b>60 passed and 12 warnings</b>; rerun tests on the final commit before making "
            "release-readiness claims.",
            styles["BodySmall"]
        ),
    ]

    sec6_grid = Table([[setup_left, setup_right]], colWidths=[256, CONTENT_W - 256])
    sec6_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(sec6_grid)
    story.append(Spacer(1, 7))

    # SECTION 07: LIMITATIONS, RESPONSIBLE USE AND REFERENCES
    story.append(make_section_header("07", "Limitations, Responsible Use and References"))
    story.append(Spacer(1, 4))

    lim_left = [
        Paragraph("Key Limitations", styles["SubHeading"]),
        Paragraph('<font color="#0D9488">•</font>  <b>Clinical validation:</b> performance on a project dataset does not establish safety for clinical decisions.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  <b>Generalization:</b> results may change across institutions, populations, measurement protocols, and prevalence levels.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  <b>Calibration:</b> discrimination metrics alone do not show whether predicted probabilities match observed event rates.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  <b>Explainability:</b> SHAP is not causal and can depend on background data and feature dependence.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  <b>Security and privacy:</b> real-world clinical data handling requires access controls, secure transport, retention rules, and privacy review.', styles["Bullet"]),
    ]

    resp_box = Table(
        [[Paragraph(
            '<font name="Helvetica-Bold" color="#0F253E">Responsible-Use Statement</font><br/>'
            'CoroVista should be presented as a research and educational prototype. Outputs should be '
            'reviewed by qualified clinicians and must not be used as the sole basis for diagnosis, '
            'treatment, or patient management. Real-world deployment would require external validation, '
            'calibration assessment, clinical workflow evaluation, privacy safeguards, and regulatory review.',
            styles["BodySmall"]
        )]],
        colWidths=[235],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), TEAL_BG),
            ("BOX", (0, 0), (-1, -1), 0.8, TEAL_ACCENT),
            ("LINEBEFORE", (0, 0), (0, -1), 3.5, TEAL_ACCENT),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    lim_right = [
        Spacer(1, 2),
        resp_box,
        Paragraph("References & Source Notes", styles["SubHeading"]),
        Paragraph('<font color="#0D9488">•</font>  <b>CoroVista repository:</b> <code>https://github.com/Nikhil9897/CoroVista</code>', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  Dataset name and metrics are reproduced from project documentation and experiment summaries.', styles["Bullet"]),
        Paragraph('<font color="#0D9488">•</font>  <b>SHAP documentation:</b> <code>https://shap.readthedocs.io/</code>', styles["Bullet"]),
    ]

    sec7_grid = Table([[lim_left, lim_right]], colWidths=[CONTENT_W - 245, 245])
    sec7_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(sec7_grid)

    doc.build(story)
    print(f"[OK] Generated clean 4-page PDF: {os.path.abspath(output_path)}")


def render_pages_to_images(pdf_path, out_dir="rendered_pages"):
    """Renders every PDF page to a 200-DPI PNG for visual layout verification."""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return

    os.makedirs(out_dir, exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    print(f"[OK] Total pages verified: {len(pdf)} pages")
    for idx, page in enumerate(pdf, start=1):
        bitmap = page.render(scale=200 / 72)
        pil_image = bitmap.to_pil()
        img_path = os.path.join(out_dir, f"page_{idx}.png")
        pil_image.save(img_path)
        print(f"  -> Saved {img_path}")


if __name__ == "__main__":
    out_pdf = "CoroVista_Technical_Documentation_Parallel_Minds_Redesigned.pdf"
    build_pdf(out_pdf)
    render_pages_to_images(out_pdf)