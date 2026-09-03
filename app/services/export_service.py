"""Export Results (Charts / Data): CSV and PDF summary generation."""

import io

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def series_to_csv(series_list):
    """series_list: list of {label, dates, values} -> CSV bytes."""
    frames = []
    for s in series_list:
        df = pd.DataFrame({"date": s["dates"], s["label"]: s["values"]})
        df = df.set_index("date")
        frames.append(df)
    combined = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    buf = io.StringIO()
    combined.to_csv(buf)
    return buf.getvalue().encode("utf-8")


def build_pdf_report(title, params, series_list, insights):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 0.4 * cm)]

    story.append(Paragraph("Search Parameters", styles["Heading2"]))
    param_rows = [[k.replace("_", " ").title(), str(v)] for k, v in params.items()]
    if param_rows:
        table = Table([["Parameter", "Value"]] + param_rows, colWidths=[6 * cm, 9 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Insights", styles["Heading2"]))
    for item in insights:
        story.append(Paragraph(f"&bull; {item}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Notice", styles["Heading2"]))
    story.append(
        Paragraph(
            "Google Trends provides relative search interest (0-100), not an "
            "absolute count of individuals affected by any condition. This "
            "report does not diagnose, and should not be interpreted as a "
            "clinical or epidemiological measurement.",
            styles["Italic"],
        )
    )

    doc.build(story)
    return buf.getvalue()
