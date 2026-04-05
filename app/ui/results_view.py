from __future__ import annotations

import streamlit as st

from app.models.analysis import AnalysisRequest, AnalysisResult, Finding, SeverityLevel
from app.models.documents import ChunkingResult, ExtractedDocument
from app.services.export import build_analysis_pdf_report
from app.services.reporting import SEVERITY_ORDER, build_scorecard_metrics


def render_results_section(
    analysis_request: AnalysisRequest,
    analysis_result: AnalysisResult,
    primary_extracted_document: ExtractedDocument,
    reference_extracted_document: ExtractedDocument | None,
    primary_chunking_result: ChunkingResult,
    reference_chunking_result: ChunkingResult | None,
) -> None:
    st.markdown('<section class="results-shell">', unsafe_allow_html=True)
    st.markdown('<div class="results-kicker">Analysis report</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="results-title">Structured Findings</h2>', unsafe_allow_html=True)
    st.markdown(
        (
            '<p class="results-copy">Review the consolidated report below. '
            'Use the filters to prioritize findings by category and severity.</p>'
        ),
        unsafe_allow_html=True,
    )

    summary_col, context_col = st.columns([1.35, 0.95], gap="large")
    with summary_col:
        _render_summary_card(analysis_result)
    with context_col:
        _render_context_card(
            analysis_request=analysis_request,
            primary_extracted_document=primary_extracted_document,
            reference_extracted_document=reference_extracted_document,
            primary_chunking_result=primary_chunking_result,
            reference_chunking_result=reference_chunking_result,
            analysis_result=analysis_result,
        )

    _render_scorecard(analysis_result)
    _render_export_actions(analysis_request, analysis_result)
    selected_severities, selected_categories = _render_filters()

    top_left, top_right = st.columns(2, gap="large")
    bottom_left, bottom_right = st.columns(2, gap="large")

    with top_left:
        _render_findings_card(
            title="Gaps",
            category="gaps",
            findings=analysis_result.gaps,
            selected_categories=selected_categories,
            selected_severities=selected_severities,
            empty_message="No material gaps were identified in this run.",
        )
    with top_right:
        _render_findings_card(
            title="Inconsistencies",
            category="inconsistencies",
            findings=analysis_result.inconsistencies,
            selected_categories=selected_categories,
            selected_severities=selected_severities,
            empty_message="No inconsistencies were identified in this run.",
        )
    with bottom_left:
        _render_findings_card(
            title="Risks",
            category="risks",
            findings=analysis_result.risks,
            selected_categories=selected_categories,
            selected_severities=selected_severities,
            empty_message="No major risks were identified in this run.",
        )
    with bottom_right:
        _render_findings_card(
            title="Recommendations",
            category="recommendations",
            findings=analysis_result.recommendations,
            selected_categories=selected_categories,
            selected_severities=selected_severities,
            empty_message="No additional recommendations were generated in this run.",
        )

    st.markdown("</section>", unsafe_allow_html=True)


def _render_summary_card(analysis_result: AnalysisResult) -> None:
    summary_text = _escape_html(analysis_result.summary or "No summary returned.").replace("\n", "<br>")
    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="result-card-title">Executive Summary</h3>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="result-card-copy">{summary_text}</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</section>", unsafe_allow_html=True)


def _render_context_card(
    *,
    analysis_request: AnalysisRequest,
    primary_extracted_document: ExtractedDocument,
    reference_extracted_document: ExtractedDocument | None,
    primary_chunking_result: ChunkingResult,
    reference_chunking_result: ChunkingResult | None,
    analysis_result: AnalysisResult,
) -> None:
    warning_count = len(primary_extracted_document.warnings) + len(
        reference_extracted_document.warnings if reference_extracted_document else []
    )
    metrics = build_scorecard_metrics(analysis_result)

    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="result-card-title">Analysis Context</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="meta-grid">
            <div class="meta-chip">
                <span class="meta-label">Primary file</span>
                <span class="meta-value">{primary_file}</span>
            </div>
            <div class="meta-chip">
                <span class="meta-label">Reference file</span>
                <span class="meta-value">{reference_file}</span>
            </div>
            <div class="meta-chip">
                <span class="meta-label">Chunks analyzed</span>
                <span class="meta-value">{chunk_count}</span>
            </div>
            <div class="meta-chip">
                <span class="meta-label">Warnings surfaced</span>
                <span class="meta-value">{warning_count}</span>
            </div>
        </div>
        """.format(
            primary_file=_escape_html(primary_extracted_document.filename),
            reference_file=_escape_html(
                reference_extracted_document.filename if reference_extracted_document else "None"
            ),
            chunk_count=_escape_html(
                _format_chunk_count(
                    analysis_request.primary_chunk_count,
                    analysis_request.reference_chunk_count,
                )
            ),
            warning_count=_escape_html(str(warning_count)),
        ),
        unsafe_allow_html=True,
    )

    st.caption(
        "Severity counts: "
        + " • ".join(
            f"{severity}: {metrics.severity_counts[severity]}" for severity in SEVERITY_ORDER
        )
    )

    if warning_count:
        warning_lines = primary_extracted_document.warnings[:]
        if reference_extracted_document:
            warning_lines.extend(reference_extracted_document.warnings)
        st.markdown(
            '<div class="warning-note">'
            + "<br>".join(_escape_html(line) for line in warning_lines)
            + "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="empty-state">No extraction warnings were surfaced for the uploaded documents.</div>',
            unsafe_allow_html=True,
        )

    st.caption(
        f"Primary preprocessing: {primary_chunking_result.chunk_count} chunks across "
        f"{primary_extracted_document.page_count} pages."
    )
    if reference_extracted_document and reference_chunking_result:
        st.caption(
            f"Reference preprocessing: {reference_chunking_result.chunk_count} chunks across "
            f"{reference_extracted_document.page_count} pages."
        )

    st.markdown("</section>", unsafe_allow_html=True)


def _render_scorecard(analysis_result: AnalysisResult) -> None:
    metrics = build_scorecard_metrics(analysis_result)

    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="result-card-title">Executive Scorecard</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Findings", str(metrics.total_findings))
    col2.metric("Highest Severity", metrics.highest_severity or "None")
    col3.metric(
        "Critical + High",
        str(metrics.severity_counts["Critical"] + metrics.severity_counts["High"]),
    )
    col4.metric("Active Categories", str(metrics.categories_with_findings))

    st.markdown("</section>", unsafe_allow_html=True)


def _render_export_actions(analysis_request: AnalysisRequest, analysis_result: AnalysisResult) -> None:
    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="result-card-title">Export Report</h3>', unsafe_allow_html=True)

    pdf_bytes = build_analysis_pdf_report(
        analysis_request=analysis_request,
        analysis_result=analysis_result,
    )
    filename_root = analysis_request.primary_document_name.rsplit(".", 1)[0]
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"{filename_root}_analysis_report.pdf",
        mime="application/pdf",
        type="primary",
    )

    st.markdown("</section>", unsafe_allow_html=True)


def _render_filters() -> tuple[list[SeverityLevel], list[str]]:
    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="result-card-title">Findings Filters</h3>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        selected_severities = st.multiselect(
            "Severity",
            options=list(SEVERITY_ORDER),
            default=list(SEVERITY_ORDER),
        )

    with right:
        selected_categories = st.multiselect(
            "Category",
            options=["gaps", "inconsistencies", "risks", "recommendations"],
            default=["gaps", "inconsistencies", "risks", "recommendations"],
            format_func=lambda item: item.capitalize(),
        )

    st.markdown("</section>", unsafe_allow_html=True)
    return selected_severities, selected_categories


def _render_findings_card(
    *,
    title: str,
    category: str,
    findings: list[Finding],
    selected_categories: list[str],
    selected_severities: list[SeverityLevel],
    empty_message: str,
) -> None:
    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown(f'<h3 class="result-card-title">{title}</h3>', unsafe_allow_html=True)

    if category not in selected_categories:
        st.markdown('<div class="empty-state">Hidden by category filter.</div>', unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)
        return

    visible_findings = [finding for finding in findings if finding.severity in selected_severities]

    if not visible_findings:
        st.markdown(f'<div class="empty-state">{empty_message}</div>', unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)
        return

    for index, finding in enumerate(visible_findings, start=1):
        with st.expander(f"{index}. [{finding.severity}] {finding.title}", expanded=False):
            st.markdown(f"**Description:** {finding.description}")
            st.markdown(f"**Evidence:** {finding.evidence}")
            st.markdown(f"**Recommendation:** {finding.recommendation}")

    st.markdown("</section>", unsafe_allow_html=True)


def _format_chunk_count(primary_chunk_count: int, reference_chunk_count: int) -> str:
    if reference_chunk_count:
        return f"{primary_chunk_count} primary / {reference_chunk_count} reference"
    return f"{primary_chunk_count} primary"


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
