from __future__ import annotations

from app.models.analysis import AnalysisRequest, AnalysisResult, Finding
from app.services.reporting import build_scorecard_metrics


def build_analysis_pdf_report(
    *,
    analysis_request: AnalysisRequest,
    analysis_result: AnalysisResult,
) -> bytes:
    lines = _build_report_lines(analysis_request, analysis_result)
    return _build_simple_pdf(lines)


def _build_report_lines(
    analysis_request: AnalysisRequest,
    analysis_result: AnalysisResult,
) -> list[str]:
    metrics = build_scorecard_metrics(analysis_result)

    lines = [
        "Policy Gap Analyzer Report",
        "",
        f"Primary file: {analysis_request.primary_document_name}",
        f"Reference file: {analysis_request.reference_document_name or 'None'}",
        "",
        "Executive Scorecard",
        f"Total findings: {metrics.total_findings}",
        f"Highest severity: {metrics.highest_severity or 'None'}",
        (
            "Severity counts: "
            f"Critical={metrics.severity_counts['Critical']}, "
            f"High={metrics.severity_counts['High']}, "
            f"Medium={metrics.severity_counts['Medium']}, "
            f"Low={metrics.severity_counts['Low']}"
        ),
        "",
        "Executive Summary",
        analysis_result.summary or "No summary returned.",
        "",
    ]

    categories = [
        ("Gaps", analysis_result.gaps),
        ("Inconsistencies", analysis_result.inconsistencies),
        ("Risks", analysis_result.risks),
        ("Recommendations", analysis_result.recommendations),
    ]

    for category_name, findings in categories:
        lines.append(category_name)
        if not findings:
            lines.append("- No findings.")
            lines.append("")
            continue

        for index, finding in enumerate(findings, start=1):
            lines.extend(_finding_lines(index, finding))
        lines.append("")

    return lines


def _finding_lines(index: int, finding: Finding) -> list[str]:
    return [
        f"{index}. [{finding.severity}] {finding.title}",
        f"   Description: {finding.description}",
        f"   Evidence: {finding.evidence}",
        f"   Recommendation: {finding.recommendation}",
    ]


def _build_simple_pdf(lines: list[str]) -> bytes:
    text_commands = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
    first_line = True

    for raw_line in lines:
        sanitized = _escape_pdf_text(raw_line)
        if first_line:
            text_commands.append(f"({sanitized}) Tj")
            first_line = False
        else:
            text_commands.append("T*")
            text_commands.append(f"({sanitized}) Tj")

    text_commands.append("ET")
    content_stream = "\n".join(text_commands).encode("utf-8")

    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        (
            f"5 0 obj << /Length {len(content_stream)} >> stream\n".encode("utf-8")
            + content_stream
            + b"\nendstream endobj\n"
        ),
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    xref_offsets = [0]

    for obj in objects:
        xref_offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in xref_offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))

    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF"
    )
    pdf.extend(trailer.encode("utf-8"))
    return bytes(pdf)


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
