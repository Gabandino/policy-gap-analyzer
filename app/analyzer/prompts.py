from __future__ import annotations

import json
from dataclasses import asdict

from app.models.analysis import ChunkAnalysis
from app.models.documents import ChunkingResult, DocumentChunk


CHUNK_ANALYSIS_SYSTEM_PROMPT = """
You are a policy analysis assistant.

Review the provided policy text carefully and return structured findings only.
Use only the supplied document text and optional reference text.
Do not claim legal certainty.
Do not invent standards, laws, or controls that are not supported by the text.
Prefer specific, practical findings over vague commentary.
If a category has no meaningful findings, return an empty list for that category.
Each finding object must include: category, severity, title, description, evidence, recommendation.
Severity must be one of: Critical, High, Medium, Low.
Evidence should cite chunk id, page context, and short supporting rationale from the provided text.
""".strip()


FINAL_ANALYSIS_SYSTEM_PROMPT = """
You are a senior policy reviewer consolidating prior chunk-level findings into one final report.

Return structured JSON only.
Use the chunk findings as the primary evidence base.
If reference-policy context is present, use it to strengthen comparisons, not to fabricate obligations.
Deduplicate overlapping findings.
Keep the summary concise and practical.
Prefer a few strong findings in each category over many repetitive ones.
Each finding object must include: category, severity, title, description, evidence, recommendation.
Severity must be one of: Critical, High, Medium, Low.
Ensure every finding has evidence tied to source chunks.
Do not claim legal certainty.
""".strip()


def build_chunk_analysis_user_prompt(
    chunk: DocumentChunk,
    primary_filename: str,
    reference_context: str | None,
    reference_filename: str | None,
) -> str:
    chunk_pages = _chunk_page_label(chunk)
    reference_block = ""
    if reference_context and reference_filename:
        reference_block = (
            f"\n\nReference policy context from {reference_filename}:\n"
            f"{reference_context}"
        )

    return (
        f"Analyze this chunk from the primary policy `{primary_filename}`.\n"
        f"Chunk id: {chunk.chunk_id}\n"
        f"Chunk pages: {chunk_pages}\n"
        f"Section heading: {chunk.section_heading or 'n/a'}\n\n"
        f"Primary policy chunk text:\n{chunk.text}"
        f"{reference_block}\n\n"
        "Return JSON with keys: summary, gaps, inconsistencies, risks, recommendations.\n"
        "Each list must contain finding objects with keys: category, severity, title, description, evidence, recommendation."
    )


def build_final_analysis_user_prompt(
    primary_result: ChunkingResult,
    chunk_analyses: list[ChunkAnalysis],
    reference_result: ChunkingResult | None,
) -> str:
    serialized_chunk_analyses = [
        {
            "chunk_id": analysis.chunk_id,
            "summary": analysis.summary,
            "gaps": [asdict(finding) for finding in analysis.gaps],
            "inconsistencies": [asdict(finding) for finding in analysis.inconsistencies],
            "risks": [asdict(finding) for finding in analysis.risks],
            "recommendations": [asdict(finding) for finding in analysis.recommendations],
        }
        for analysis in chunk_analyses
    ]

    reference_note = "No reference policy was provided."
    if reference_result:
        reference_note = (
            f"Reference policy filename: {reference_result.filename}\n"
            f"Reference chunk count: {reference_result.chunk_count}"
        )

    return (
        f"Consolidate the chunk-level findings for the primary policy `{primary_result.filename}`.\n"
        f"Primary chunk count: {primary_result.chunk_count}\n"
        f"{reference_note}\n\n"
        "Chunk findings JSON:\n"
        f"{json.dumps(serialized_chunk_analyses, indent=2)}\n\n"
        "Return JSON with keys: summary, gaps, inconsistencies, risks, recommendations.\n"
        "Each category list must contain finding objects with keys: category, severity, title, description, evidence, recommendation.\n"
        "The summary should be one concise paragraph. Each list should contain distinct, concrete findings."
    )


def _chunk_page_label(chunk: DocumentChunk) -> str:
    if chunk.start_page is None or chunk.end_page is None:
        return "unknown"
    if chunk.start_page == chunk.end_page:
        return f"page {chunk.start_page}"
    return f"pages {chunk.start_page}-{chunk.end_page}"
