"""Orbitly SalesOS deck for Meridian Freight Systems (fixture for RAG parsing tests).

Builds a 11-slide PPTX with: dark cover/closing, stat callouts, 2 native charts,
1 matplotlib graph image, pricing/comparison/security tables, rollout diagram.
Palette: indigo primary, teal accent, white content background.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

HERE = os.path.dirname(os.path.abspath(__file__))

# palette
BG      = RGBColor(0xFF, 0xFF, 0xFF)
DARK    = RGBColor(0x14, 0x1B, 0x33)   # deep indigo — cover/closing
PRIMARY = RGBColor(0x1B, 0x2A, 0x4A)
PRIMARY_LT = RGBColor(0x3E, 0x53, 0x7E)
ACCENT  = RGBColor(0x0D, 0x94, 0x88)   # teal
TEXT    = RGBColor(0x1E, 0x29, 0x3B)
MUTED   = RGBColor(0x64, 0x74, 0x8B)
TINT    = RGBColor(0xF1, 0xF5, 0xF9)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Segoe UI"

W, H = Inches(13.333), Inches(7.5)


def tb(slide, x, y, w, h, text, size=18, color=TEXT, bold=False, align=PP_ALIGN.LEFT,
       font=FONT, line_spacing=1.0):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = ln
        p.alignment = align
        p.line_spacing = line_spacing
        for r in p.runs:
            r.font.name = font
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = color
    return box


def rect(slide, x, y, w, h, fill, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    sh.adjustments[0] = 0.06
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def chart_style(chart):
    chart.has_title = False
    ca = chart.category_axis
    va = chart.value_axis
    for ax in (ca, va):
        ax.tick_labels.font.size = Pt(11)
        ax.tick_labels.font.color.rgb = MUTED
        ax.tick_labels.font.name = FONT
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    ca.has_major_gridlines = False


# ── matplotlib graph image (for "image/graph parsing" tests) ────────────────
def make_graph_png():
    q = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
    before = [61, 60, 62, 59, 60, 61]
    after = [61, 63, 71, 79, 84, 87]
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=160)
    ax.plot(q, before, marker="o", linewidth=2.2, color="#94A3B8", label="Before Orbitly")
    ax.plot(q, after, marker="o", linewidth=2.6, color="#0D9488", label="With Orbitly SalesOS")
    ax.axvline(x=1.0, color="#1B2A4A", linestyle="--", linewidth=1.2)
    ax.annotate("Orbitly onboarded", xy=(1.0, 63), xytext=(1.4, 40),
                fontsize=10, color="#1B2A4A",
                arrowprops=dict(arrowstyle="->", color="#1B2A4A"))
    ax.set_ylabel("Forecast accuracy (%)", fontsize=10)
    ax.set_ylim(35, 95)
    ax.legend(frameon=False, fontsize=10, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E2E8F0", linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    p = os.path.join(HERE, "img_forecast_trend.png")
    fig.savefig(p, facecolor="white")
    plt.close(fig)
    return p


GRAPH = make_graph_png()

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]

def add_slide(dark=False):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = DARK if dark else BG
    return s

# ── 1. COVER (dark) ──────────────────────────────────────────────────────────
s = add_slide(dark=True)
tb(s, Inches(0.9), Inches(2.2), Inches(11.5), Inches(1.6),
   "Orbitly SalesOS", 66, WHITE, bold=True)
tb(s, Inches(0.9), Inches(3.6), Inches(11.5), Inches(0.9),
   "Revenue intelligence for freight & logistics sales teams", 26, RGBColor(0x94, 0xA3, 0xB8))
tb(s, Inches(0.9), Inches(5.4), Inches(11.5), Inches(1.2),
   "Prepared for Meridian Freight Systems  ·  Sahla Thasnim, VP Sales Operations\nAugust 2026  ·  Confidential", 15,
   RGBColor(0x94, 0xA3, 0xB8), line_spacing=1.3)
d = rect(s, Inches(0.9), Inches(1.85), Inches(1.1), Inches(0.12), ACCENT)

# ── 2. THE PROBLEM (stat callout) ────────────────────────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "Monday forecast day is broken", 34, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.35), Inches(11.9), Inches(0.6),
   "Meridian runs 340 reps across India and the EU on a spreadsheet rollup.", 17, MUTED)
rect(s, Inches(0.7), Inches(2.3), Inches(4.6), Inches(3.6), TINT)
tb(s, Inches(0.95), Inches(2.75), Inches(4.1), Inches(1.5), "6%", 96, ACCENT, bold=True)
tb(s, Inches(0.95), Inches(4.5), Inches(4.1), Inches(1.2),
   "missed last quarter's number —\nthe slippage was visible two\nweeks before it was acted on", 15, TEXT)
stats = [
    ("60%", "forecast accuracy today —\nevery deal scored by gut feel"),
    ("9 hrs", "per rep per week lost to\nmanual CRM data entry"),
    ("6 mo", "for a new AE to reach\nfull quota productivity"),
]
for i, (num, lab) in enumerate(stats):
    y = Inches(2.3 + i * 1.25)
    tb(s, Inches(5.8), y, Inches(2.2), Inches(1.0), num, 40, PRIMARY, bold=True)
    tb(s, Inches(8.0), y + Inches(0.08), Inches(4.8), Inches(1.0), lab, 14, TEXT, line_spacing=1.1)
tb(s, Inches(0.7), Inches(6.45), Inches(11.9), Inches(0.5),
   "Source: Meridian discovery call, Aug 2026 (MER-ORBT-DISC-0042)", 11, MUTED)

# ── 3. WHAT ORBITLY DOES (three cards) ───────────────────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "One platform, three engines", 34, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.35), Inches(11.9), Inches(0.6),
   "Every engine feeds the same deal graph — calls, email, and CRM stages.", 17, MUTED)
cards = [
    ("Conversation\nIntelligence", "Every call transcribed and scored against your playbook. Objections,\ncompetitors, and next steps extracted automatically — zero rep data entry."),
    ("Forecast\nIntelligence", "Every open deal scored weekly with a confidence number and reasons.\nCustomers move from ~60% forecast accuracy to 85%+."),
    ("Coaching\n& Ramp", "Managers review 2 minutes of highlights instead of 40 minutes of audio.\nNew AEs reach full quota in 3 months instead of 6."),
]
for i, (title, body) in enumerate(cards):
    x = Inches(0.7 + i * 4.15)
    rect(s, x, Inches(2.35), Inches(3.85), Inches(3.5), TINT)
    tb(s, x + Inches(0.3), Inches(2.7), Inches(3.3), Inches(1.0), title, 22, PRIMARY, bold=True)
    tb(s, x + Inches(0.3), Inches(4.0), Inches(3.3), Inches(1.7), body, 13.5, TEXT, line_spacing=1.15)
    d = rect(s, x + Inches(0.3), Inches(2.62), Inches(0.55), Inches(0.09), ACCENT)

# ── 4. CONVERSATION INTELLIGENCE (native bar chart) ─────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "Conversation Intelligence: manager time collapses", 30, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.4), Inches(11.9), Inches(0.6),
   "Call scoring against your playbook replaces full-call listening. Win rate lifts +12% after two quarters.",
   16, MUTED)
cd = CategoryChartData()
cd.categories = ["Review time per rep (min)", "Ramp to quota (months)", "CRM updates (hrs/wk)"]
cd.add_series("Before", (40, 6, 9))
cd.add_series("With Orbitly", (2, 3, 0.5))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.7), Inches(2.25),
                        Inches(7.6), Inches(4.2), cd)
chart = gf.chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.include_in_layout = False
chart.legend.font.size = Pt(12)
chart.plots[0].gap_width = 90
chart_style(chart)
rect(s, Inches(8.7), Inches(2.25), Inches(4.0), Inches(4.2), TINT)
tb(s, Inches(9.0), Inches(2.6), Inches(3.4), Inches(0.9), "+12%", 54, ACCENT, bold=True)
tb(s, Inches(9.0), Inches(3.6), Inches(3.4), Inches(2.6),
   "win rate after two quarters,\nacross the customer base.\n\nObjection and competitor\ndetection runs on every call\nautomatically.", 14, TEXT, line_spacing=1.15)
tb(s, Inches(0.7), Inches(6.75), Inches(11.9), Inches(0.4),
   "Source: Orbitly customer base aggregate, FY2026", 11, MUTED)

# ── 5. FORECAST INTELLIGENCE (matplotlib graph image) ───────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "Forecast accuracy: 60% to 87% in two quarters", 30, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.4), Inches(11.9), Inches(0.6),
   "Weekly deal scoring with per-deal confidence and reasons — not a gut rollup. Typical customer trajectory below.",
   16, MUTED)
s.shapes.add_picture(GRAPH, Inches(0.7), Inches(2.3), width=Inches(7.9))
rect(s, Inches(9.0), Inches(2.3), Inches(3.6), Inches(3.9), TINT)
tb(s, Inches(9.3), Inches(2.65), Inches(3.0), Inches(3.4),
   "What drives the lift:\n\n– Every deal scored\n   weekly, not monthly\n– Slippage flagged in\n   week 8, not week 11\n– Reasons attached to\n   every confidence\n   number", 14, TEXT, line_spacing=1.12)
tb(s, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.4),
   "Source: Orbitly Forecast Intelligence cohort, customers onboarded H1-FY2026 (illustrative)", 11, MUTED)

# ── 6. PRICING (table) ───────────────────────────────────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "Pricing for Meridian — 340 seats", 34, PRIMARY, bold=True)
rows = [
    ["", "Team", "Growth  (recommended)", "Enterprise"],
    ["Price / seat / year", "$480", "$600", "Custom"],
    ["Conversation Intelligence", "Included", "Included", "Included"],
    ["Forecast Intelligence", "—", "Included", "Included"],
    ["Adoption guarantee", "—", "Included", "Included"],
    ["Data residency (India / EU)", "—", "In-region add-on", "Included"],
    ["340-seat annual list", "$163,200", "$204,000", "Custom"],
]
tbl_shape = s.shapes.add_table(len(rows), 4, Inches(0.7), Inches(1.7), Inches(11.9), Inches(4.2))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(3.6)
for c in range(1, 4):
    tbl.columns[c].width = Inches(2.76)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri, ci)
        cell.text = val
        cell.margin_top = cell.margin_bottom = Pt(6)
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT
        p.font.size = Pt(13 if ri else 14)
        p.font.bold = (ri == 0) or (ci == 0)
        if ri == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = PRIMARY
            p.font.color.rgb = WHITE
        elif ri == 2 and ci == 2:
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0xCC, 0xFB, 0xF1)
            p.font.color.rgb = TEXT
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = TINT if ri % 2 == 0 else WHITE
            p.font.color.rgb = TEXT
tbl.cell(2, 2).text_frame.paragraphs[0].font.bold = True
tb(s, Inches(0.7), Inches(6.2), Inches(11.9), Inches(0.9),
   "Three-year commit unlocks a 15% ceiling → $173,400/year at 340 seats. Team tier excludes Forecast Intelligence —\nMeridian's headline pain — so Growth is the right fit.", 15, TEXT, line_spacing=1.2)

# ── 7. ROLLOUT (numbered diagram) ────────────────────────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "340 reps live in under two months", 34, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.35), Inches(11.9), Inches(0.6),
   "Everything lives inside Salesforce — no separate rep login, no six-month project.", 17, MUTED)
steps = [
    ("1", "Day 1", "Salesforce connected,\nbi-directional sync on"),
    ("2", "Week 1", "SAP billing connector\ningests back-office data"),
    ("3", "Weeks 2–11", "40-rep pilot, 60 days —\ngates signed into the plan"),
    ("4", "Weeks 12–16", "Full 340-rep rollout,\nrep-led kickoff webinar"),
]
for i, (n, when, body) in enumerate(steps):
    x = Inches(0.7 + i * 3.18)
    circ = s.shapes.add_shape(1, x + Inches(1.05), Inches(2.5), Inches(0.85), Inches(0.85))
    circ.fill.solid(); circ.fill.fore_color.rgb = ACCENT
    circ.line.fill.background()
    circ.text_frame.paragraphs[0].text = n
    circ.text_frame.paragraphs[0].font.size = Pt(26)
    circ.text_frame.paragraphs[0].font.bold = True
    circ.text_frame.paragraphs[0].font.color.rgb = WHITE
    circ.text_frame.paragraphs[0].font.name = FONT
    tb(s, x, Inches(3.6), Inches(2.95), Inches(0.5), when, 18, PRIMARY, bold=True, align=PP_ALIGN.CENTER)
    tb(s, x, Inches(4.15), Inches(2.95), Inches(1.4), body, 13.5, TEXT, align=PP_ALIGN.CENTER, line_spacing=1.15)
rect(s, Inches(0.7), Inches(5.9), Inches(11.9), Inches(1.0), TINT)
tb(s, Inches(1.0), Inches(6.12), Inches(11.3), Inches(0.7),
   "Pilot gates: 80% weekly-active reps by week 4  ·  80% forecast accuracy on pilot deals  ·  <15 min manager review per rep per week",
   14.5, PRIMARY, bold=True)

# ── 8. PROOF — TransCarry case (native column chart) ────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "TransCarry: same industry, similar seat count", 32, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.4), Inches(11.9), Inches(0.6),
   "1,100-rep logistics operator, onboarded Q4-FY2025. Monthly active rep adoption after kickoff:",
   16, MUTED)
cd = CategoryChartData()
cd.categories = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5"]
cd.add_series("Weekly active reps (%)", (62, 74, 81, 84, 86))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.2),
                        Inches(7.6), Inches(4.1), cd)
chart = gf.chart
chart.has_legend = False
chart.plots[0].gap_width = 60
plot = chart.plots[0]
plot.vary_by_categories = False
chart.series[0].format.fill.solid()
chart.series[0].format.fill.fore_color.rgb = ACCENT
chart_style(chart)
rect(s, Inches(8.7), Inches(2.2), Inches(4.0), Inches(4.1), TINT)
for i, (num, lab) in enumerate([("$4.2M", "pipeline pulled forward\nin two quarters"),
                                ("3 mo", "ramp to quota, down\nfrom six"),
                                ("7 mo", "ROI payback at\nMeridian's headcount")]):
    y = Inches(2.5 + i * 1.3)
    tb(s, Inches(9.0), y, Inches(3.4), Inches(0.7), num, 32, PRIMARY, bold=True)
    tb(s, Inches(9.0), y + Inches(0.55), Inches(3.4), Inches(0.7), lab, 12.5, TEXT)
tb(s, Inches(0.7), Inches(6.6), Inches(11.9), Inches(0.4),
   "Source: TransCarry account review, Q2-FY2026", 11, MUTED)

# ── 9. SECURITY (table) ──────────────────────────────────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "Security & compliance", 34, PRIMARY, bold=True)
tb(s, Inches(0.7), Inches(1.4), Inches(11.9), Inches(0.6),
   "Everything below ships in the security pack — SOC 2 report, ISO certificate, DPA, residency options.",
   16, MUTED)
rows = [
    ["Control", "Status", "Detail"],
    ["SOC 2 Type II", "Current", "Annual audit; report in security pack"],
    ["ISO 27001", "Current", "Certificate included"],
    ["Data residency", "India + EU", "Enterprise tier included; Growth via in-region add-on"],
    ["Model training", "Never", "No customer call data trains any model"],
    ["DPA", "Standard", "EU SCCs where applicable"],
]
tbl_shape = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(2.25), Inches(11.9), Inches(3.6))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(3.0)
tbl.columns[1].width = Inches(2.4)
tbl.columns[2].width = Inches(6.5)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri, ci)
        cell.text = val
        cell.margin_top = cell.margin_bottom = Pt(7)
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT
        p.font.size = Pt(14)
        p.font.bold = (ri == 0) or (ci == 0)
        if ri == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = PRIMARY
            p.font.color.rgb = WHITE
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = TINT if ri % 2 == 0 else WHITE
            p.font.color.rgb = TEXT

# ── 10. VS SALESLANE (comparison) ────────────────────────────────────────────
s = add_slide()
tb(s, Inches(0.7), Inches(0.55), Inches(11.9), Inches(0.8),
   "Orbitly vs Saleslane — compare on the pains you opened with", 28, PRIMARY, bold=True)
rows = [
    ["Capability", "Orbitly", "Saleslane"],
    ["Conversation capture & scoring", "Included", "Included"],
    ["Forecast scoring vs SAP billing data", "Included", "—"],
    ["Adoption guarantee (contracted)", "Included", "—"],
    ["India / EU data residency", "Enterprise / add-on", "EU only"],
    ["Price (annual, per seat)", "$600 (Growth)", "$420"],
]
tbl_shape = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.8), Inches(11.9), Inches(3.9))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(4.9)
tbl.columns[1].width = Inches(3.5)
tbl.columns[2].width = Inches(3.5)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri, ci)
        cell.text = val
        cell.margin_top = cell.margin_bottom = Pt(7)
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT
        p.font.size = Pt(14)
        p.font.bold = (ri == 0) or (ci == 0)
        if ri == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = PRIMARY
            p.font.color.rgb = WHITE
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = TINT if ri % 2 == 0 else WHITE
            p.font.color.rgb = TEXT
tb(s, Inches(0.7), Inches(6.0), Inches(11.9), Inches(1.0),
   "Saleslane is a fine conversation-capture tool. On forecast accuracy and ramp — the two pains Meridian\nopened the call with — it doesn't play.", 15.5, TEXT, line_spacing=1.2)

# ── 11. NEXT STEPS (dark closing) ────────────────────────────────────────────
s = add_slide(dark=True)
tb(s, Inches(0.9), Inches(0.9), Inches(11.5), Inches(0.9),
   "Agreed next steps", 40, WHITE, bold=True)
items = [
    ("Friday", "Orbitly sends: security pack, pilot plan with 3 gates, TransCarry ROI model, draft intro email for Priya Nair"),
    ("Next week", "Meridian: security review kickoff with Mrunal"),
    ("Week after", "15-minute intro: Sahla → Priya Nair (CFO)"),
    ("Aug 12", "40-rep pilot kickoff — $0 cost, gates signed into the plan"),
    ("End of Q3", "Target signature after the Q1 budget freeze lifts"),
]
for i, (when, what) in enumerate(items):
    y = Inches(2.1 + i * 0.95)
    tb(s, Inches(0.9), y, Inches(2.1), Inches(0.6), when, 18, ACCENT, bold=True)
    tb(s, Inches(3.1), y, Inches(9.4), Inches(0.8), what, 17, WHITE)
tb(s, Inches(0.9), Inches(6.8), Inches(11.5), Inches(0.5),
   "Orbitly  ·  revenue intelligence for logistics sales  ·  confidential", 12, RGBColor(0x94, 0xA3, 0xB8))

out = os.path.join(HERE, "orbitly_sales_deck_meridian.pptx")
prs.save(out)
print(f"WROTE {out} — {len(prs.slides.__iter__.__self__._sldIdLst)} slides")
