import io
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#17365D")
GRAY = colors.HexColor("#D9D9D9")


def build_report_card_text(report_data):
    lines = [
        "Generated Student Report Card",
        f"Student Name: {report_data['student_name']}",
        f"Roll Number: {report_data['roll_number']}",
        f"Semester: {report_data['semester']}",
        f"Academic Year: {report_data['academic_year']}",
        f"Total Marks: {report_data['total_marks']} / {report_data['maximum_marks']}",
        f"Percentage: {report_data['percentage']}%",
        f"Average Marks: {report_data['average_marks']}",
        f"Overall Grade: {report_data['overall_grade']}",
        f"Overall Pass/Fail: {report_data['overall_result']}",
        f"Performance Category: {report_data['performance_category']}",
        f"Remarks: {report_data['remarks']}",
    ]
    for subject in report_data["subjects"]:
        lines.append(
            f"{subject['name']} | Marks: {subject['marks']} | "
            f"Grade: {subject['grade']} | Status: {subject['status']}"
        )
    return "\n".join(lines)


def generate_report_card_pdf(report_data):
    pdf_buffer = io.BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Student Report Card",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=NAVY,
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=8,
    )
    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        textColor=NAVY,
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=6,
        spaceAfter=5,
    )
    body_style = styles["BodyText"]

    story = [
        Paragraph("Generated Student Report Card", title_style),
        Paragraph("Student Information", heading_style),
    ]

    student_table = Table(
        [
            ["Student Name", escape(str(report_data["student_name"]))],
            ["Roll Number", escape(str(report_data["roll_number"]))],
            ["Semester", escape(str(report_data["semester"]))],
            ["Academic Year", escape(str(report_data["academic_year"]))],
        ],
        colWidths=[42 * mm, 126 * mm],
    )
    student_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF3F8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([student_table, Spacer(1, 5), Paragraph("Academic Results", heading_style)])

    subject_table_data = [["Subject", "Marks Obtained", "Grade", "Status"]]
    for subject in report_data["subjects"]:
        subject_table_data.append([
            escape(str(subject["name"])),
            str(subject["marks"]),
            escape(str(subject["grade"])),
            escape(str(subject["status"])),
        ])

    subject_table = Table(
        subject_table_data,
        colWidths=[85 * mm, 30 * mm, 22 * mm, 31 * mm],
        repeatRows=1,
    )
    subject_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([subject_table, Spacer(1, 7), Paragraph("Overall Result Summary", heading_style)])

    summary_table = Table([
        ["Total Marks", f"{report_data['total_marks']} / {report_data['maximum_marks']}"],
        ["Percentage", f"{report_data['percentage']}%"],
        ["Average Marks", str(report_data["average_marks"])],
        ["Overall Grade", escape(str(report_data["overall_grade"]))],
        ["Overall Pass/Fail", escape(str(report_data["overall_result"]))],
        ["Performance Category", escape(str(report_data["performance_category"]))],
        ["Remarks", escape(str(report_data["remarks"]))],
    ], colWidths=[42 * mm, 126 * mm])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF3F8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(summary_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "This document is a generated student report card.",
        ParagraphStyle(
            "GeneratedNote",
            parent=body_style,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#666666"),
            fontSize=8,
        ),
    ))

    document.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
