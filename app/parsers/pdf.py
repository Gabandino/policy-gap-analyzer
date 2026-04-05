from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.models.documents import ExtractedDocument, ExtractedPage


MIN_MEANINGFUL_CHARACTER_COUNT = 80
logger = logging.getLogger(__name__)


class PdfExtractionError(Exception):
    """Raised when a PDF cannot produce usable text for downstream analysis."""


@dataclass(slots=True)
class RawPdfExtraction:
    page_count: int
    pages: list[ExtractedPage]
    text: str
    character_count: int
    warnings: list[str]


def extract_pdf_text(file_bytes: bytes, filename: str, role: str) -> ExtractedDocument:
    logger.info("Starting PDF extraction for %s (%s).", filename, role)
    raw_extraction = _read_pdf(file_bytes, filename)
    logger.info(
        "Completed PDF extraction for %s with %s pages, %s characters, %s warnings.",
        filename,
        raw_extraction.page_count,
        raw_extraction.character_count,
        len(raw_extraction.warnings),
    )
    return ExtractedDocument(
        filename=filename,
        role=role,
        page_count=raw_extraction.page_count,
        extracted_character_count=raw_extraction.character_count,
        text=raw_extraction.text,
        pages=raw_extraction.pages,
        warnings=raw_extraction.warnings,
    )


def _read_pdf(file_bytes: bytes, filename: str) -> RawPdfExtraction:
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except PdfReadError as exc:
        logger.warning("Malformed PDF encountered during extraction: %s", filename)
        raise PdfExtractionError(
            f"{filename} could not be read as a valid PDF."
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected PDF open failure for %s.", filename)
        raise PdfExtractionError(
            f"{filename} could not be opened for text extraction."
        ) from exc

    page_count = len(reader.pages)
    if page_count == 0:
        raise PdfExtractionError(f"{filename} does not contain any pages.")

    extracted_pages: list[ExtractedPage] = []
    warnings: list[str] = []

    for page_index, page in enumerate(reader.pages, start=1):
        try:
            raw_text = page.extract_text() or ""
        except Exception:
            raw_text = ""
            logger.warning("Text extraction failed for %s page %s.", filename, page_index)
            warnings.append(
                f"Page {page_index} could not be read cleanly and may be missing text."
            )

        normalized_text = normalize_extracted_text(raw_text)
        extracted_pages.append(
            ExtractedPage(
                page_number=page_index,
                text=normalized_text,
                character_count=len(normalized_text),
            )
        )

        if not normalized_text:
            logger.info("No extractable text found for %s page %s.", filename, page_index)
            warnings.append(f"Page {page_index} did not contain extractable text.")

    combined_text = "\n\n".join(page.text for page in extracted_pages if page.text).strip()
    character_count = len(combined_text)

    if not combined_text:
        logger.warning("No extractable text produced for %s.", filename)
        raise PdfExtractionError(
            f"{filename} did not produce any extractable text. "
            "This usually means the PDF is scanned, image-based, or malformed."
        )

    if character_count < MIN_MEANINGFUL_CHARACTER_COUNT:
        warnings.append(
            f"{filename} produced very little text ({character_count} characters). "
            "The PDF may be scanned, image-based, or poorly structured."
        )

    return RawPdfExtraction(
        page_count=page_count,
        pages=extracted_pages,
        text=combined_text,
        character_count=character_count,
        warnings=_dedupe_warnings(warnings),
    )


def normalize_extracted_text(text: str) -> str:
    if not text:
        return ""

    cleaned_text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned_text = re.sub(r"[ \t\f\v]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    normalized_paragraphs: list[str] = []
    for paragraph in re.split(r"\n\s*\n", cleaned_text):
        lines = [re.sub(r"\s+", " ", line).strip() for line in paragraph.splitlines()]
        paragraph_text = " ".join(line for line in lines if line)
        paragraph_text = re.sub(r"\s{2,}", " ", paragraph_text).strip()
        if paragraph_text:
            normalized_paragraphs.append(paragraph_text)

    return "\n\n".join(normalized_paragraphs).strip()


def _dedupe_warnings(warnings: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()

    for warning in warnings:
        if warning in seen:
            continue
        seen.add(warning)
        deduped.append(warning)

    return deduped
