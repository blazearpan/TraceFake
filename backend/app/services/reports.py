from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from backend.app.core.config import settings

def generate_pdf(result: dict) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = f"tracefake_report_{timestamp}.pdf"
    path = Path(settings.reports_dir) / safe_name
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("TRACEFAKE", styles["Title"]),
        Paragraph("Trace the Link. Detect the Threat.", styles["Heading2"]),
        Spacer(1, 8),
        Paragraph(f"<b>Analyzed URL:</b> {result['url']}", styles["BodyText"]),
        Paragraph(f"<b>Classification:</b> {result['classification']}", styles["BodyText"]),
        Paragraph(f"<b>Risk Score:</b> {result['risk_score']} / 100", styles["BodyText"]),
        Paragraph(f"<b>ML Score:</b> {result['ml_score']} / 100", styles["BodyText"]),
        Paragraph(f"<b>Rule Score:</b> {result['rule_score']} / 100", styles["BodyText"]),
        Paragraph(f"<b>Model:</b> {result['model_name']}", styles["BodyText"]),
        Spacer(1, 10),
        Paragraph("Detection Reasons", styles["Heading2"]),
    ]
    reason_data = [["Severity", "Source", "Reason"]]
    reason_data += [[r["severity"], r["source"], r["description"]] for r in result["reasons"]]
    table = Table(reason_data, colWidths=[25*mm, 25*mm, 125*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [table, Spacer(1, 10), Paragraph("Technical Features", styles["Heading2"])]
    feature_data = [["Feature", "Value", "Risk"]] + [[f["name"], f["value"], f["risk"]] for f in result["features"]]
    ft = Table(feature_data, colWidths=[70*mm, 50*mm, 30*mm], repeatRows=1)
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 7.5),
    ]))
    story += [ft, Spacer(1, 10), Paragraph("Recommendations", styles["Heading2"])]
    for item in result["recommendations"]:
        story.append(Paragraph("• " + item, styles["BodyText"]))
    story += [Spacer(1, 10), Paragraph("Disclaimer", styles["Heading2"]),
              Paragraph("TraceFake provides a probabilistic risk assessment based on the available model and static URL indicators. A SAFE result is not proof that a destination is harmless, and a PHISHING result should be independently verified. No phishing detector can guarantee perfect detection.", styles["BodyText"])]
    doc.build(story)
    return path
