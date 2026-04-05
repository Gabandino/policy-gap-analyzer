from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from app.analyzer.pipeline import PolicyAnalysisError, analyze_policy_documents
from app.config import AppConfig
from app.models.analysis import AnalysisRequest, AnalysisResult
from app.models.documents import ChunkingResult, ExtractedDocument, UploadedDocument
from app.parsers.pdf import PdfExtractionError
from app.services.chunking import chunk_extracted_document
from app.services.extraction import extract_uploaded_document
from app.ui.results_view import render_results_section
from app.ui.state import initialize_session_state

logger = logging.getLogger(__name__)


def render_upload_section(config: AppConfig) -> None:
    initialize_session_state()
    _render_hero(config)

    left_col, right_col = st.columns([1.35, 0.9], gap="large")

    with left_col:
        st.markdown('<section class="panel-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="panel-title">Upload Documents</h2>', unsafe_allow_html=True)
        st.markdown(
            (
                '<p class="panel-copy">Start with your current policy. '
                'You can also add a reference policy to support comparison later.</p>'
            ),
            unsafe_allow_html=True,
        )

        primary_file = st.file_uploader(
            "Your Policy",
            type=list(config.allowed_extensions),
            accept_multiple_files=False,
            help=f"Required. Upload a PDF up to {config.max_upload_size_mb} MB.",
        )
        reference_file = st.file_uploader(
            "Reference Policy",
            type=list(config.allowed_extensions),
            accept_multiple_files=False,
            help="Optional. Upload a PDF used as comparison context.",
        )

        submission_clicked = st.button("Analyze", type="primary")

        if submission_clicked:
            _handle_submission(primary_file, reference_file, config)

        _render_submission_feedback()
        st.markdown("</section>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<section class="panel-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="panel-title">Current Scope</h2>', unsafe_allow_html=True)
        st.markdown(
            (
                '<p class="panel-copy">This shell now covers Milestone 5: upload validation, '
                'preprocessing, staged LLM analysis, and a polished results screen for structured findings.</p>'
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="feature-grid">
                <div class="feature-chip">PDF upload validation</div>
                <div class="feature-chip">Page-by-page extraction</div>
                <div class="feature-chip">Whitespace normalization</div>
                <div class="feature-chip">Overlapping chunks</div>
                <div class="feature-chip">Two-stage LLM analysis</div>
                <div class="feature-chip">Result cards and empty states</div>
            </div>
            <p class="status-note">
                Next milestone: harden the end-to-end flow with more testing and clearer recovery paths.
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</section>", unsafe_allow_html=True)


def _render_hero(config: AppConfig) -> None:
    st.markdown(
        f"""
        <section class="hero-card">
            <div class="hero-kicker">Policy Review MVP</div>
            <h1 class="hero-title">{config.app_title}</h1>
            <p class="hero-copy">{config.app_subtitle}</p>
            <div class="feature-grid">
                <div class="feature-chip">Upload your policy PDF</div>
                <div class="feature-chip">Add an optional reference PDF</div>
                <div class="feature-chip">Prepare for structured AI analysis</div>
                <div class="feature-chip">Demo-ready purple and blue UI</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _handle_submission(
    primary_file: Any,
    reference_file: Any,
    config: AppConfig,
) -> None:
    st.session_state.last_submission_error = None
    st.session_state.last_analysis_error = None

    primary_error = _validate_uploaded_file(primary_file, "Your Policy", config, required=True)
    reference_error = _validate_uploaded_file(
        reference_file,
        "Reference Policy",
        config,
        required=False,
    )

    if primary_error or reference_error:
        logger.warning("Upload validation failed: %s", primary_error or reference_error)
        st.session_state.last_submission_error = primary_error or reference_error
        _clear_processed_state()
        return

    primary_document = _to_uploaded_document(primary_file, "primary")
    reference_document = _to_uploaded_document(reference_file, "reference") if reference_file else None
    logger.info(
        "Upload accepted. Primary=%s Reference=%s",
        primary_document.filename,
        reference_document.filename if reference_document else "none",
    )

    try:
        with st.spinner("Extracting and chunking your uploaded PDF..."):
            primary_extracted_document = extract_uploaded_document(primary_file, primary_document)
            reference_extracted_document = (
                extract_uploaded_document(reference_file, reference_document)
                if reference_file and reference_document
                else None
            )
            primary_chunking_result = chunk_extracted_document(
                primary_extracted_document,
                config.default_chunk_size,
                config.default_chunk_overlap,
            )
            reference_chunking_result = (
                chunk_extracted_document(
                    reference_extracted_document,
                    config.default_chunk_size,
                    config.default_chunk_overlap,
                )
                if reference_extracted_document
                else None
            )
    except (PdfExtractionError, ValueError) as exc:
        logger.warning("Preprocessing failed: %s", exc)
        st.session_state.last_submission_error = (
            f"{exc} Review the uploaded file and try again."
        )
        _clear_processed_state()
        return

    st.session_state.primary_document = primary_document
    st.session_state.reference_document = reference_document
    st.session_state.primary_extracted_document = primary_extracted_document
    st.session_state.reference_extracted_document = reference_extracted_document
    st.session_state.primary_chunking_result = primary_chunking_result
    st.session_state.reference_chunking_result = reference_chunking_result

    if not config.openai_api_key:
        logger.warning("Analysis skipped because OPENAI_API_KEY is missing.")
        st.session_state.analysis_request = None
        st.session_state.analysis_result = None
        st.session_state.last_analysis_error = (
            "OPENAI_API_KEY is required to run the analysis pipeline. "
            "Add it to your environment or .env file, then rerun the analysis."
        )
        return

    try:
        with st.spinner("Analyzing policy chunks and consolidating findings..."):
            analysis_request, analysis_result = analyze_policy_documents(
                primary_result=primary_chunking_result,
                reference_result=reference_chunking_result,
                api_key=config.openai_api_key,
                model=config.openai_model,
            )
    except PolicyAnalysisError as exc:
        logger.warning("Policy analysis failed: %s", exc)
        st.session_state.analysis_request = None
        st.session_state.analysis_result = None
        st.session_state.last_analysis_error = str(exc)
        return

    logger.info("Analysis completed successfully for %s.", primary_document.filename)
    st.session_state.analysis_request = analysis_request
    st.session_state.analysis_result = analysis_result


def _render_submission_feedback() -> None:
    error_message = st.session_state.get("last_submission_error")
    if error_message:
        st.error(error_message)
        return

    primary_document: UploadedDocument | None = st.session_state.get("primary_document")
    reference_document: UploadedDocument | None = st.session_state.get("reference_document")
    primary_extracted_document: ExtractedDocument | None = st.session_state.get(
        "primary_extracted_document"
    )
    reference_extracted_document: ExtractedDocument | None = st.session_state.get(
        "reference_extracted_document"
    )
    primary_chunking_result: ChunkingResult | None = st.session_state.get("primary_chunking_result")
    reference_chunking_result: ChunkingResult | None = st.session_state.get("reference_chunking_result")
    analysis_request: AnalysisRequest | None = st.session_state.get("analysis_request")
    analysis_result: AnalysisResult | None = st.session_state.get("analysis_result")
    analysis_error: str | None = st.session_state.get("last_analysis_error")

    if not primary_document or not primary_extracted_document or not primary_chunking_result:
        st.info(
            "Upload a primary policy PDF and click Analyze to run extraction, chunking, and structured analysis."
        )
        return

    st.success(
        f"Document processing complete. Primary file ready: {primary_document.filename}"
    )

    if analysis_error:
        st.error(analysis_error)
        st.caption(
            "Preprocessing completed successfully, but the LLM analysis step did not return a final report."
        )
        return

    if analysis_request and analysis_result:
        render_results_section(
            analysis_request=analysis_request,
            analysis_result=analysis_result,
            primary_extracted_document=primary_extracted_document,
            reference_extracted_document=reference_extracted_document,
            primary_chunking_result=primary_chunking_result,
            reference_chunking_result=reference_chunking_result,
        )
        with st.expander("View preprocessing details", expanded=False):
            _render_extraction_summary(primary_extracted_document, "Primary policy")
            _render_chunking_summary(primary_chunking_result)

            if reference_document and reference_extracted_document and reference_chunking_result:
                _render_extraction_summary(reference_extracted_document, "Reference policy")
                _render_chunking_summary(reference_chunking_result)
    else:
        st.info("Analysis has not been run yet.")


def _validate_uploaded_file(
    uploaded_file: Any,
    label: str,
    config: AppConfig,
    *,
    required: bool,
) -> str | None:
    if required and uploaded_file is None:
        return f"{label} is required. Upload a PDF before continuing."

    if uploaded_file is None:
        return None

    metadata = _to_uploaded_document(uploaded_file, "validation")
    if metadata.extension not in config.allowed_extensions:
        return f"{label} must be a PDF file."

    max_size_bytes = config.max_upload_size_mb * 1024 * 1024
    if metadata.size_bytes > max_size_bytes:
        return (
            f"{label} exceeds the {config.max_upload_size_mb} MB limit. "
            "Upload a smaller PDF."
        )

    return None


def _to_uploaded_document(uploaded_file: Any, role: str) -> UploadedDocument:
    return UploadedDocument(
        filename=uploaded_file.name,
        content_type=getattr(uploaded_file, "type", None),
        size_bytes=getattr(uploaded_file, "size", 0),
        role=role,
    )


def _render_extraction_summary(extracted_document: ExtractedDocument, label: str) -> None:
    st.markdown(f"**{label}**")
    st.caption(
        f"{extracted_document.filename} - {extracted_document.page_count} pages - "
        f"{extracted_document.extracted_character_count} extracted characters"
    )

    if extracted_document.warnings:
        for warning in extracted_document.warnings:
            st.warning(warning)
    else:
        st.info("No extraction warnings detected.")


def _render_chunking_summary(chunking_result: ChunkingResult) -> None:
    st.caption(
        f"{chunking_result.chunk_count} chunks prepared for "
        f"{chunking_result.source_document_label.lower()}."
    )

    if chunking_result.discarded_chunk_count:
        st.caption(
            f"Skipped {chunking_result.discarded_chunk_count} duplicate or near-empty chunk candidate(s)."
        )

    with st.expander(f"Preview {chunking_result.source_document_label.lower()} chunks", expanded=False):
        preview_chunks = chunking_result.chunks[:3]
        for chunk in preview_chunks:
            page_label = _format_chunk_pages(chunk.start_page, chunk.end_page)
            heading_label = f"Section: {chunk.section_heading}" if chunk.section_heading else "Section: n/a"
            st.markdown(f"`{chunk.chunk_id}` - {page_label} - {chunk.character_count} characters")
            st.caption(heading_label)
            st.code(chunk.text[:400], language="text")


def _format_chunk_pages(start_page: int | None, end_page: int | None) -> str:
    if start_page is None or end_page is None:
        return "Pages unavailable"
    if start_page == end_page:
        return f"Page {start_page}"
    return f"Pages {start_page}-{end_page}"


def _clear_processed_state() -> None:
    st.session_state.primary_document = None
    st.session_state.reference_document = None
    st.session_state.primary_extracted_document = None
    st.session_state.reference_extracted_document = None
    st.session_state.primary_chunking_result = None
    st.session_state.reference_chunking_result = None
    st.session_state.analysis_request = None
    st.session_state.analysis_result = None
    st.session_state.last_analysis_error = None
