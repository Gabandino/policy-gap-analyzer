from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.models.documents import ChunkingResult, DocumentChunk, ExtractedDocument


MIN_CHUNK_CHARACTER_COUNT = 60
logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TextBlock:
    text: str
    page_number: int
    section_heading: str | None = None


def chunk_extracted_document(
    document: ExtractedDocument,
    chunk_size: int,
    chunk_overlap: int,
) -> ChunkingResult:
    logger.info(
        "Starting chunking for %s with chunk_size=%s and chunk_overlap=%s.",
        document.filename,
        chunk_size,
        chunk_overlap,
    )
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")
    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")
    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    source_label = _source_label_for_role(document.role)
    blocks = _build_text_blocks(document, chunk_size)

    if not blocks and document.text:
        blocks = [
            TextBlock(
                text=document.text.strip(),
                page_number=1,
                section_heading=None,
            )
        ]

    chunks: list[DocumentChunk] = []
    current_blocks: list[TextBlock] = []
    seen_chunk_texts: set[str] = set()
    discarded_chunk_count = 0

    for block in blocks:
        while current_blocks and _joined_length(current_blocks) + 2 + len(block.text) > chunk_size:
            discarded_chunk_count += _append_chunk(
                chunks,
                current_blocks,
                source_label,
                document.role,
                seen_chunk_texts,
            )
            current_blocks = _overlap_seed(current_blocks, chunk_overlap)

            while current_blocks and _joined_length(current_blocks) + 2 + len(block.text) > chunk_size:
                current_blocks = current_blocks[1:]

        current_blocks.append(block)

    if current_blocks:
        discarded_chunk_count += _append_chunk(
            chunks,
            current_blocks,
            source_label,
            document.role,
            seen_chunk_texts,
        )

    result = ChunkingResult(
        filename=document.filename,
        role=document.role,
        source_document_label=source_label,
        chunks=chunks,
        discarded_chunk_count=discarded_chunk_count,
    )
    logger.info(
        "Completed chunking for %s with %s chunks and %s discarded chunk candidates.",
        document.filename,
        result.chunk_count,
        discarded_chunk_count,
    )
    return result


def _build_text_blocks(document: ExtractedDocument, chunk_size: int) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    active_heading: str | None = None
    prefix_heading_on_next_block = False

    for page in document.pages:
        paragraphs = [paragraph.strip() for paragraph in page.text.split("\n\n") if paragraph.strip()]
        for paragraph in paragraphs:
            if _looks_like_heading(paragraph):
                active_heading = paragraph
                prefix_heading_on_next_block = True
                continue

            block_text = paragraph
            if prefix_heading_on_next_block and active_heading:
                block_text = f"{active_heading}\n\n{paragraph}"
                prefix_heading_on_next_block = False

            block = TextBlock(
                text=block_text,
                page_number=page.page_number,
                section_heading=active_heading,
            )
            blocks.extend(_split_oversized_block(block, chunk_size))

    return blocks


def _split_oversized_block(block: TextBlock, chunk_size: int) -> list[TextBlock]:
    if len(block.text) <= chunk_size:
        return [block]

    sentences = _split_into_sentences(block.text)
    if len(sentences) == 1:
        return _split_by_words(block, chunk_size)

    split_blocks: list[TextBlock] = []
    current_parts: list[str] = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)
        separator_length = 1 if current_parts else 0
        if current_parts and current_length + separator_length + sentence_length > chunk_size:
            split_blocks.append(
                TextBlock(
                    text=" ".join(current_parts).strip(),
                    page_number=block.page_number,
                    section_heading=block.section_heading,
                )
            )
            current_parts = [sentence]
            current_length = sentence_length
            continue

        current_parts.append(sentence)
        current_length += separator_length + sentence_length

    if current_parts:
        split_blocks.append(
            TextBlock(
                text=" ".join(current_parts).strip(),
                page_number=block.page_number,
                section_heading=block.section_heading,
            )
        )

    refined_blocks: list[TextBlock] = []
    for split_block in split_blocks:
        if len(split_block.text) <= chunk_size:
            refined_blocks.append(split_block)
        else:
            refined_blocks.extend(_split_by_words(split_block, chunk_size))

    return refined_blocks


def _split_by_words(block: TextBlock, chunk_size: int) -> list[TextBlock]:
    words = block.text.split()
    split_blocks: list[TextBlock] = []
    current_words: list[str] = []
    current_length = 0

    for word in words:
        word_length = len(word)
        separator_length = 1 if current_words else 0
        if current_words and current_length + separator_length + word_length > chunk_size:
            split_blocks.append(
                TextBlock(
                    text=" ".join(current_words),
                    page_number=block.page_number,
                    section_heading=block.section_heading,
                )
            )
            current_words = [word]
            current_length = word_length
            continue

        current_words.append(word)
        current_length += separator_length + word_length

    if current_words:
        split_blocks.append(
            TextBlock(
                text=" ".join(current_words),
                page_number=block.page_number,
                section_heading=block.section_heading,
            )
        )

    return split_blocks


def _append_chunk(
    chunks: list[DocumentChunk],
    blocks: list[TextBlock],
    source_label: str,
    role: str,
    seen_chunk_texts: set[str],
) -> int:
    text = "\n\n".join(block.text for block in blocks if block.text).strip()
    if not text:
        return 1

    if len(text) < MIN_CHUNK_CHARACTER_COUNT and chunks:
        previous_chunk = chunks[-1]
        if text not in previous_chunk.text:
            previous_chunk.text = f"{previous_chunk.text}\n\n{text}".strip()
            previous_chunk.end_page = blocks[-1].page_number
        return 0

    if text in seen_chunk_texts:
        return 1

    seen_chunk_texts.add(text)
    chunk_number = len(chunks) + 1
    chunks.append(
        DocumentChunk(
            chunk_id=f"{role}-{chunk_number:03d}",
            source_document_label=source_label,
            text=text,
            start_page=blocks[0].page_number,
            end_page=blocks[-1].page_number,
            section_heading=blocks[0].section_heading,
        )
    )
    return 0


def _joined_length(blocks: list[TextBlock]) -> int:
    if not blocks:
        return 0
    return sum(len(block.text) for block in blocks) + (2 * (len(blocks) - 1))


def _overlap_seed(blocks: list[TextBlock], chunk_overlap: int) -> list[TextBlock]:
    if chunk_overlap <= 0:
        return []

    overlap_blocks: list[TextBlock] = []
    current_length = 0

    for block in reversed(blocks):
        separator_length = 2 if overlap_blocks else 0
        proposed_length = current_length + separator_length + len(block.text)
        if overlap_blocks and proposed_length > chunk_overlap:
            break
        if not overlap_blocks and len(block.text) > chunk_overlap:
            break
        overlap_blocks.append(block)
        current_length = proposed_length

    overlap_blocks.reverse()
    return overlap_blocks


def _looks_like_heading(text: str) -> bool:
    normalized = " ".join(text.split()).strip()
    if not normalized or len(normalized) > 90:
        return False
    if "\n" in text:
        return False

    heading_patterns = (
        re.fullmatch(r"\d+(\.\d+)*[.)]?\s+[A-Z][A-Za-z0-9 /,&()-]+", normalized),
        re.fullmatch(r"[A-Z][A-Z0-9 /,&()-]{3,}", normalized),
        re.fullmatch(r"[A-Z][A-Za-z0-9 /,&()-]{2,}", normalized),
    )
    if any(heading_patterns):
        return not normalized.endswith((".", "?", "!", ":"))

    return False


def _split_into_sentences(text: str) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    return sentences or [text.strip()]


def _source_label_for_role(role: str) -> str:
    if role == "primary":
        return "Primary policy"
    if role == "reference":
        return "Reference policy"
    return role.replace("_", " ").title()
