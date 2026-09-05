#!/usr/bin/env python3
"""
RideWire Motorcycle Job Aid PDF builder (REAL implementation, ReportLab).

Builds one job-aid PDF per real Harley-Davidson DTC, combining:
- The verified code description/causes/first-check/sources (moto_codes_verified.json)
- The generic reference schematic (consensus_runs/moto/<key>_schematic.png)
- The 3-model consensus report (consensus_runs/moto/report_<key>.json)

Honesty framing throughout: this is AI-assisted research support, not a
certified repair procedure, and the "agreement" figures are literal keyword
overlap on a single query - not a validated accuracy score. Same standard
already applied to the P0171 car job aid.
"""
import json
import os
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)

DIAG_DIR = os.path.dirname(__file__)
MOTO_DIR = os.path.join(DIAG_DIR, "consensus_runs", "moto")
VERIFIED_CODES_PATH = os.path.join(DIAG_DIR, "moto_codes_verified.json")
OUT_DIR = os.path.join(DIAG_DIR, "..", "..", "job_aids", "motorcycle")

TEAL = HexColor("#01696F")
DARKTEAL = HexColor("#1B474D")
NEUTRAL = HexColor("#28251D")
MUTED = HexColor("#7A7974")
WARN = HexColor("#964219")
BG = HexColor("#F7F6F2")

CODE_KEY_TO_DTC = {
    "p0562": "P0562",
    "p0131": "P0131",
    "ckp": "P0371 / P0372 / P0374",
    "abs": "C1032 / C1034",
}


def load_verified_code(dtc_code):
    with open(VERIFIED_CODES_PATH) as f:
        data = json.load(f)
    for entry in data["codes"]:
        if entry["code"] == dtc_code:
            return entry
    raise KeyError(dtc_code)


def styles_set():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("JATitle", parent=ss["Title"], fontName="Helvetica-Bold",
                           fontSize=19, leading=23, textColor=DARKTEAL, spaceAfter=4))
    ss.add(ParagraphStyle("JASubtitle", parent=ss["Normal"], fontName="Helvetica-Oblique",
                           fontSize=10, leading=13, textColor=MUTED, spaceAfter=10))
    ss.add(ParagraphStyle("JAH2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                           fontSize=13, leading=16, textColor=DARKTEAL, spaceBefore=14, spaceAfter=6))
    ss.add(ParagraphStyle("JABody", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=9.5, leading=13.5, textColor=NEUTRAL, spaceAfter=6, alignment=TA_LEFT))
    ss.add(ParagraphStyle("JABullet", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=9.5, leading=13.5, textColor=NEUTRAL, leftIndent=14,
                           bulletIndent=2, spaceAfter=4))
    ss.add(ParagraphStyle("JAHonesty", parent=ss["Normal"], fontName="Helvetica-Oblique",
                           fontSize=8.7, leading=12, textColor=WARN, spaceAfter=6))
    ss.add(ParagraphStyle("JAFootnote", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=7.7, leading=10.5, textColor=MUTED, spaceAfter=3))
    ss.add(ParagraphStyle("JACell", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=8.3, leading=11, textColor=NEUTRAL))
    ss.add(ParagraphStyle("JACellHead", parent=ss["Normal"], fontName="Helvetica-Bold",
                           fontSize=8.5, leading=11, textColor=HexColor("#FFFFFF")))
    return ss


def header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(MUTED)
    canvas_obj.drawString(0.75 * inch, 0.45 * inch,
                           "RideWire AI-Assisted Diagnostic Job Aid \u2014 research support only, not a certified repair procedure")
    canvas_obj.drawRightString(letter[0] - 0.75 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas_obj.restoreState()


def build_pdf(code_key):
    dtc_code = CODE_KEY_TO_DTC[code_key]
    verified = load_verified_code(dtc_code)
    with open(os.path.join(MOTO_DIR, f"report_{code_key}.json")) as f:
        report = json.load(f)

    ss = styles_set()
    story = []

    short_title = dtc_code
    story.append(Paragraph(f"RideWire Job Aid \u2014 {short_title}", ss["JATitle"]))
    story.append(Paragraph(verified["description"].split(".")[0] + ".", ss["JASubtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#D4D1CA"), spaceAfter=10))

    story.append(Paragraph(
        "This job aid is AI-assisted research support compiled from real Harley-Davidson "
        "service bulletins, diagnostic manuals, and owner/technician forum reports, cross-checked "
        "by three independent AI models. It is <b>not</b> a certified repair procedure and does not "
        "replace the vehicle's factory service manual. Always verify against manufacturer documentation "
        "before performing repairs.",
        ss["JAHonesty"]))

    story.append(Paragraph("Platform", ss["JAH2"]))
    story.append(Paragraph(verified["platform"], ss["JABody"]))

    story.append(Paragraph("Code Description<super>1</super>", ss["JAH2"]))
    story.append(Paragraph(verified["description"], ss["JABody"]))

    story.append(Paragraph("Likely Causes (verified sources)", ss["JAH2"]))
    for cause in verified["likely_causes"]:
        story.append(Paragraph(f"\u2022 {cause}", ss["JABullet"]))

    story.append(Paragraph("Recommended First Check<super>2</super>", ss["JAH2"]))
    story.append(Paragraph(verified["first_check"], ss["JABody"]))

    story.append(Paragraph(f"Source confidence: {verified['confidence_note']}", ss["JAFootnote"]))

    # Schematic
    img_path = os.path.join(MOTO_DIR, f"{code_key}_schematic.png")
    story.append(Paragraph("Reference Schematic", ss["JAH2"]))
    story.append(Paragraph(
        "Generic principle-level diagram \u2014 not a manufacturer-exact wiring diagram for any specific "
        "make/model/year. Always verify against the factory service manual.", ss["JAFootnote"]))
    img = Image(img_path, width=6.6 * inch, height=6.6 * inch * (900 / 1350) if False else 4.35 * inch)
    story.append(img)

    # Consensus section
    story.append(Paragraph("Multi-AI Consensus (3 independent models)", ss["JAH2"]))
    story.append(Paragraph(
        "\u201cAgreement\u201d below is a plain keyword-overlap check on each model's own wording for this "
        "single query \u2014 it is NOT a validated machine-learning accuracy score and has not been checked "
        "against confirmed repair outcomes. Read each model's own words in the table for the actual reasoning.",
        ss["JAHonesty"]))

    header = [Paragraph("Model", ss["JACellHead"]), Paragraph("Primary Root Cause", ss["JACellHead"]),
              Paragraph("Urgency", ss["JACellHead"]), Paragraph("Recommended First Check", ss["JACellHead"])]
    rows = [header]
    for model_name, d in report["per_model_diagnosis"].items():
        rows.append([
            Paragraph(model_name, ss["JACell"]),
            Paragraph(d["primary_root_cause"], ss["JACell"]),
            Paragraph(d["urgency"], ss["JACell"]),
            Paragraph(d["recommended_first_check"], ss["JACell"]),
        ])
    table = Table(rows, colWidths=[1.05 * inch, 2.15 * inch, 0.7 * inch, 2.3 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARKTEAL),
        ("FONTSIZE", (0, 0), (-1, -1), 8.3),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D4D1CA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Root cause agreement:</b> {report['root_cause_agreement']}", ss["JABody"]))
    story.append(Paragraph(f"<b>Urgency values reported:</b> {', '.join(report['urgency_values'])} "
                            f"({'all 3 models agree' if report['urgency_agreement'] else 'models differ'})",
                            ss["JABody"]))

    # Sources / footnotes
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#D4D1CA"), spaceAfter=6))
    story.append(Paragraph("Sources", ss["JAH2"]))
    for i, url in enumerate(verified["sources"], start=1):
        story.append(Paragraph(f'{i}. <a href="{url}" color="blue">{url}</a>', ss["JAFootnote"]))
    story.append(Paragraph(
        "Superscript 1-2 in the text above refer to the same verified source set backing the code "
        "description and first-check procedure, drawn from the sources listed here.", ss["JAFootnote"]))

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{code_key}_job_aid.pdf")
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        title=f"RideWire Job Aid - {dtc_code}",
        author="Perplexity Computer",
        topMargin=0.65 * inch, bottomMargin=0.7 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"saved {out_path}")


if __name__ == "__main__":
    keys = sys.argv[1:] if len(sys.argv) > 1 else list(CODE_KEY_TO_DTC.keys())
    for k in keys:
        build_pdf(k)
