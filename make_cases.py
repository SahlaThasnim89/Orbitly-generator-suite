"""Orbitly case study pack — PDF (reportlab platypus).

Three case studies with paragraphs, ROI tables, a matplotlib comparison chart,
and a customer-quote sidebar — built to exercise document parsing (tables,
images, multi-column-ish layout).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))

INDIGO = colors.HexColor("#1B2A4A")
TEAL = colors.HexColor("#0D9488")
MUTED = colors.HexColor("#64748B")
TINT = colors.HexColor("#F1F5F9")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                    textColor=INDIGO, fontSize=20, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    textColor=INDIGO, fontSize=14, spaceBefore=14, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=ss["BodyText"], fontName="Helvetica",
                      fontSize=10, leading=14.5, alignment=TA_LEFT)
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.5, textColor=MUTED,
                     alignment=TA_CENTER, spaceBefore=2)
QUOTE = ParagraphStyle("QUOTE", parent=BODY, fontName="Helvetica-Oblique",
                       fontSize=10.5, leading=15, leftIndent=18, rightIndent=18,
                       textColor=INDIGO, spaceBefore=8, spaceAfter=4)
KPI = ParagraphStyle("KPI", parent=ss["Title"], fontName="Helvetica-Bold",
                     textColor=TEAL, fontSize=22, alignment=TA_CENTER, spaceBefore=10)


def make_chart():
    fig, ax = plt.subplots(figsize=(6.6, 3.0), dpi=160)
    groups = ["Forecast\naccuracy", "Ramp to\nquota (mo, inv.)", "Manager review\n(min/wk, inv.)"]
    before = [60, 6, 40]
    after = [85, 3, 2]
    x = range(len(groups))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], before, w, color="#94A3B8", label="Before")
    b2 = ax.bar([i + w / 2 for i in x], after, w, color="#0D9488", label="After Orbitly")
    for bars in (b1, b2):
        for b in bars:
            ax.annotate(f"{b.get_height():g}", (b.get_x() + b.get_width() / 2, b.get_height()),
                        ha="center", va="bottom", fontsize=9)
    ax.set_xticks(list(x)); ax.set_xticklabels(groups, fontsize=9)
    ax.set_ylabel("Value per group (see axis note)", fontsize=9)
    ax.set_title("TransCarry: before vs after Orbitly (10 quarters)", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", color="#E2E8F0", linewidth=0.6); ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.01, -0.24, "Note: 'inv.' metrics are inverted so lower bars = better (months, minutes).",
            transform=ax.transAxes, fontsize=8, color="#64748B")
    fig.tight_layout()
    p = os.path.join(HERE, "img_case_before_after.png")
    fig.savefig(p, facecolor="white")
    plt.close(fig)
    return p


CHART = make_chart()

story = []

# ── Cover-ish header ────────────────────────────────────────────────────────
story.append(Paragraph("Orbitly Customer Case Study Pack", H1))
story.append(Paragraph("Three reference accounts · FY2026 · Prepared for Meridian Freight Systems "
                       "· Document ID: CS-PACK-2026-Q3 · Confidential", 
                       ParagraphStyle("sub", parent=BODY, fontSize=9.5, textColor=MUTED)))
story.append(Spacer(1, 8 * mm))

# ── Case study 1: TransCarry ────────────────────────────────────────────────
story.append(Paragraph("Case Study 1 — TransCarry Logistics", H2))
story.append(Paragraph(
    "<b>Profile.</b> TransCarry is a pan-Asian contract-logistics operator running 1,100 sales reps "
    "across 9 countries, selling freight capacity and warehousing contracts to mid-market "
    "manufacturers. Like most logistics sellers, their pipeline lives in Salesforce while the "
    "real signals — detention disputes, lane-rate objections, seasonal capacity commitments — "
    "live on phone calls. They onboarded Orbitly SalesOS (Growth tier) in Q4-FY2025.", BODY))
story.append(Paragraph(
    "<b>Problem.</b> Forecast calls were a weekly argument: regional managers each defended a "
    "spreadsheet number, and the aggregate landed within ±15% of the actual quarter. Ramp was "
    "the second tax — new account executives needed six months to reach quota, and the same "
    "onboarding content was re-delivered manually by an enablement team of three.", BODY))
story.append(Paragraph(
    "<b>What changed.</b> After two quarters on Orbitly: forecast accuracy moved from 60% to 85% "
    "(median absolute error on the weekly commit); ramp-to-quota compressed to 3 months; manager "
    "call-review time dropped from 40 minutes per rep per week to under 2 minutes of scored "
    "highlights; and $4.2M of at-risk pipeline was pulled forward when forecast flags surfaced "
    "stalling deals eight weeks before quarter close.", BODY))

kpi = Table([
    [Paragraph("$4.2M", KPI), Paragraph("3 mo", KPI), Paragraph("+12%", KPI)],
    [Paragraph("pipeline pulled forward", CAP), Paragraph("ramp to quota (was 6)", CAP),
     Paragraph("win rate after 2 quarters", CAP)],
], colWidths=[58 * mm, 58 * mm, 58 * mm])
kpi.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), TINT),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 1), (-1, 1), 0),
]))
story.append(kpi)
story.append(Spacer(1, 6 * mm))
story.append(Paragraph("ROI at Meridian-like scale", H2))
roi = Table([
    ["Line item", "Value", "Basis"],
    ["Annual license (340 seats, Growth)", "$204,000", "$600/seat list; $173,400 with 15% three-year commit"],
    ["Recovered selling time", "$1.63M/yr", "8.5 hrs/rep/wk saved × 340 reps × $110/hr loaded cost"],
    ["Ramp acceleration value", "$0.9M/yr", "3 months earlier quota × ~60 new AEs/yr × $5K/mo margin"],
    ["Forecast-error reduction", "$0.7M/yr", "±15% → ±5% error on a $48M annual number"],
    ["Payback", "7 months", "conservative: selling-time value only"],
], colWidths=[62 * mm, 30 * mm, 82 * mm])
roi.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TINT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(roi)
story.append(Paragraph("Table 1 — TransCarry ROI model, normalized to Meridian's 340-seat scale (illustrative).", CAP))
story.append(Spacer(1, 5 * mm))
story.append(Image(CHART, width=150 * mm, height=150 * mm * 3.0 / 6.6))
story.append(Paragraph("Figure 1 — Before/after on the three headline metrics. 'inv.' = inverted so lower is better.", CAP))
story.append(Paragraph(
    "\u201CThe Monday forecast fight is gone. The number the machine puts up is the number we "
    "actually land within five points.\u201D — Dana Whitfield, CRO, TransCarry", QUOTE))
story.append(PageBreak())

# ── Case study 2: Helios Medical ────────────────────────────────────────────
story.append(Paragraph("Case Study 2 — Helios Medical Devices", H2))
story.append(Paragraph(
    "<b>Profile.</b> Helios sells surgical equipment into hospital networks through a 600-rep "
    "field team with an unusually long cycle — procurement committees, compliance reviews, and "
    "an average 9-month deal. They onboarded in Q2-FY2025, Enterprise tier with EU residency.", BODY))
story.append(Paragraph(
    "<b>Problem.</b> Committee deals died silently: a single unanswered compliance objection in "
    "month five could stall a $400K opportunity without anyone noticing for a quarter. Coaching "
    "coverage was 1 manager to 14 reps, so call review was effectively a lottery.", BODY))
story.append(Paragraph(
    "<b>Outcome.</b> Orbitly's objection taxonomy surfaced stalled-committee deals 6 weeks earlier "
    "on median; win rate on deals above $250K rose from 22% to 31% over three quarters; and every "
    "rep now receives a weekly scored highlight reel, giving coaching coverage that doesn't depend "
    "on manager headcount. Security review passed with EU residency on the Enterprise tier.", BODY))
outc = Table([
    ["Metric", "Before", "After 3 quarters"],
    ["Win rate, deals > $250K", "22%", "31%"],
    ["Median stall-detection lag", "9 weeks", "3 weeks"],
    ["Coaching coverage", "1:14 (manager-bound)", "1:1 (automated weekly)"],
    ["Committee-deal forecast accuracy", "58%", "86%"],
], colWidths=[62 * mm, 48 * mm, 64 * mm])
outc.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TINT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(outc)
story.append(Paragraph("Table 2 — Helios Medical outcomes, FY2026 cohort review.", CAP))
story.append(Paragraph(
    "\u201CIt found the compliance objection buried on a 47-minute call in week three that we "
    "didn't find until the deal had been dead for a month.\u201D — Marcus Reinhardt, VP Sales, Helios", QUOTE))
story.append(Spacer(1, 6 * mm))

# ── Case study 3: Solstice SaaS ─────────────────────────────────────────────
story.append(Paragraph("Case Study 3 — Solstice Software (velocity sales)", H2))
story.append(Paragraph(
    "<b>Profile.</b> A 90-rep inside-sales team selling developer tooling on 3-week cycles — the "
    "opposite end of the motion from TransCarry. Solstice runs Team tier plus the Conversation "
    "Intelligence add-on and validates whether the platform works at high volume rather than "
    "high deal value. They process roughly 8,000 calls per day.", BODY))
story.append(Paragraph(
    "<b>Outcome.</b> At velocity scale, the value shifts from forecasting to messaging: playbook "
    "scoring showed that reps who mentioned the customer's onboarding effort in the first 10 "
    "minutes closed 1.7× more often, so the pitch was re-ordered team-wide in week one of "
    "analysis. Objection-to-playbook mapping cut discounting from an 18% average to 11% by "
    "routing the pricing objection to a standard proof script.", BODY))
vtab = Table([
    ["Signal discovered", "Action taken", "Result"],
    ["Early onboarding-effort mention → 1.7× close rate", "Pitch re-ordered in week 1", "+23% team close rate in a quarter"],
    ["Pricing objection without proof script → −31% win", "Auto-surfaced proof snippets to reps", "Avg discount 18% → 11%"],
    ["Top-decile demo structure", "Extracted and templatized", "New-hire ramp 5.5 → 3.5 months"],
], colWidths=[64 * mm, 48 * mm, 62 * mm])
vtab.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TINT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(vtab)
story.append(Paragraph("Table 3 — Solstice velocity-account signals, FY2026.", CAP))

story.append(Spacer(1, 8 * mm))
story.append(Paragraph(
    "Methodology note: cohort metrics are medians across customers onboarded in the stated "
    "window, measured on the Orbitly platform. Figures labeled illustrative are modeled, not "
    "audited. Full methodology and customer references are available under NDA.", 
    ParagraphStyle("meth", parent=BODY, fontSize=8.5, textColor=MUTED)))

out = os.path.join(HERE, "orbitly_case_studies.pdf")
doc = SimpleDocTemplate(out, pagesize=A4,
                        leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=16 * mm,
                        title="Orbitly Case Study Pack FY2026",
                        author="Orbitly")
doc.build(story)
print(f"WROTE {out}")
