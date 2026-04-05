from __future__ import annotations

import logging
import re

from app.analyzer.client import AnalysisClientError, OpenAIAnalysisClient
from app.analyzer.prompts import (
    CHUNK_ANALYSIS_SYSTEM_PROMPT,
    FINAL_ANALYSIS_SYSTEM_PROMPT,
    build_chunk_analysis_user_prompt,
    build_final_analysis_user_prompt,
)
from app.analyzer.schemas import ANALYSIS_RESULT_JSON_SCHEMA
from app.models.analysis import AnalysisRequest, AnalysisResult, ChunkAnalysis
from app.models.documents import ChunkingResult, DocumentChunk

logger = logging.getLogger(__name__)


class PolicyAnalysisError(Exception):
    """Raised when the policy analysis pipeline cannot produce a structured report."""


def analyze_policy_documents(
    *,
    primary_result: ChunkingResult,
    reference_result: ChunkingResult | None,
    api_key: str,
    model: str,
) -> tuple[AnalysisRequest, AnalysisResult]:
    if not api_key:
        raise PolicyAnalysisError(
            "OPENAI_API_KEY is required to run policy analysis. Add it to your environment or .env file."
        )
    if not primary_result.chunks:
        raise PolicyAnalysisError("The primary policy does not contain any chunks to analyze.")

    client = OpenAIAnalysisClient(api_key=api_key, model=model)
    request = AnalysisRequest(
        primary_document_name=primary_result.filename,
        reference_document_name=reference_result.filename if reference_result else None,
        primary_chunk_count=primary_result.chunk_count,
        reference_chunk_count=reference_result.chunk_count if reference_result else 0,
    )

    try:
        logger.info(
            "Starting policy analysis for %s with %s primary chunks and %s reference chunks.",
            primary_result.filename,
            primary_result.chunk_count,
            reference_result.chunk_count if reference_result else 0,
        )
        chunk_analyses = [
            _analyze_chunk(client, chunk, primary_result.filename, reference_result)
            for chunk in primary_result.chunks
        ]

        final_payload = client.generate_structured_output(
            system_prompt=FINAL_ANALYSIS_SYSTEM_PROMPT,
            user_prompt=build_final_analysis_user_prompt(
                primary_result=primary_result,
                chunk_analyses=chunk_analyses,
                reference_result=reference_result,
            ),
            schema_name="policy_analysis_result",
            schema=ANALYSIS_RESULT_JSON_SCHEMA,
            max_output_tokens=1800,
        )
    except AnalysisClientError as exc:
        logger.warning("Analysis failed for %s: %s", primary_result.filename, exc)
        raise PolicyAnalysisError(str(exc)) from exc

    final_result = AnalysisResult.from_payload(final_payload)
    if not _has_analysis_content(final_result):
        logger.warning("Empty structured analysis result returned for %s.", primary_result.filename)
        raise PolicyAnalysisError("The model returned an empty structured analysis result.")

    logger.info("Completed policy analysis for %s.", primary_result.filename)
    return request, final_result


def _analyze_chunk(
    client: OpenAIAnalysisClient,
    chunk: DocumentChunk,
    primary_filename: str,
    reference_result: ChunkingResult | None,
) -> ChunkAnalysis:
    reference_context = None
    reference_filename = None
    if reference_result and reference_result.chunks:
        selected_chunks = _select_reference_chunks(chunk, reference_result.chunks)
        if selected_chunks:
            reference_context = "\n\n".join(
                f"{selected.chunk_id} ({_chunk_page_label(selected)}):\n{selected.text}"
                for selected in selected_chunks
            )
            reference_filename = reference_result.filename

    payload = client.generate_structured_output(
        system_prompt=CHUNK_ANALYSIS_SYSTEM_PROMPT,
        user_prompt=build_chunk_analysis_user_prompt(
            chunk=chunk,
            primary_filename=primary_filename,
            reference_context=reference_context,
            reference_filename=reference_filename,
        ),
        schema_name="policy_chunk_analysis",
        schema=ANALYSIS_RESULT_JSON_SCHEMA,
        max_output_tokens=1200,
    )
    return ChunkAnalysis.from_payload(chunk.chunk_id, payload)


def _select_reference_chunks(
    primary_chunk: DocumentChunk,
    reference_chunks: list[DocumentChunk],
) -> list[DocumentChunk]:
    primary_tokens = _tokenize(primary_chunk.text)
    if not primary_tokens:
        return reference_chunks[:1]

    scored_chunks: list[tuple[int, int, DocumentChunk]] = []
    for index, candidate in enumerate(reference_chunks):
        candidate_tokens = _tokenize(candidate.text)
        overlap_score = len(primary_tokens & candidate_tokens)
        scored_chunks.append((overlap_score, -index, candidate))

    scored_chunks.sort(reverse=True)
    selected: list[DocumentChunk] = []
    total_characters = 0

    for score, _, candidate in scored_chunks:
        if not selected and score == 0:
            selected.append(candidate)
            break

        if score <= 0:
            continue

        if total_characters and total_characters + len(candidate.text) > 2200:
            continue

        selected.append(candidate)
        total_characters += len(candidate.text)
        if len(selected) >= 2:
            break

    return selected


def _tokenize(text: str) -> set[str]:
    stop_words = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "must",
        "will",
        "your",
        "have",
        "into",
        "their",
        "policy",
        "shall",
    }
    tokens = set(re.findall(r"[a-zA-Z]{4,}", text.lower()))
    return {token for token in tokens if token not in stop_words}


def _chunk_page_label(chunk: DocumentChunk) -> str:
    if chunk.start_page is None or chunk.end_page is None:
        return "pages unavailable"
    if chunk.start_page == chunk.end_page:
        return f"page {chunk.start_page}"
    return f"pages {chunk.start_page}-{chunk.end_page}"


def _has_analysis_content(result: AnalysisResult) -> bool:
    return bool(
        result.summary
        or result.gaps
        or result.inconsistencies
        or result.risks
        or result.recommendations
    )
