from __future__ import annotations

import streamlit as st

from app.models.analysis import AnalysisRequest, AnalysisResult
from app.models.documents import ChunkingResult, ExtractedDocument


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
            'The summary and category cards are designed for quick demo scanning, '
            'while preprocessing details remain available underneath.</p>'
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
        )

    top_left, top_right = st.columns(2, gap="large")
    bottom_left, bottom_right = st.columns(2, gap="large")

    with top_left:
        _render_findings_card(
            title="Gaps",
            items=analysis_result.gaps,
            empty_message="No material gaps were identified in this run.",
        )
    with top_right:
        _render_findings_card(
            title="Inconsistencies",
            items=analysis_result.inconsistencies,
            empty_message="No inconsistencies were identified in this run.",
        )
    with bottom_left:
        _render_findings_card(
            title="Risks",
            items=analysis_result.risks,
            empty_message="No major risks were identified in this run.",
        )
    with bottom_right:
        _render_findings_card(
            title="Recommendations",
            items=analysis_result.recommendations,
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
) -> None:
    warning_count = len(primary_extracted_document.warnings) + len(
        reference_extracted_document.warnings if reference_extracted_document else []
    )

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


def _render_findings_card(title: str, items: list[str], empty_message: str) -> None:
    st.markdown('<section class="result-card">', unsafe_allow_html=True)
    st.markdown(f'<h3 class="result-card-title">{title}</h3>', unsafe_allow_html=True)

    if not items:
        st.markdown(f'<div class="empty-state">{empty_message}</div>', unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)
        return

    for index, item in enumerate(items, start=1):
        st.markdown(f"{index}. {item}")

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
