from __future__ import annotations

import logging

from app.models.documents import ExtractedDocument, UploadedDocument
from app.parsers.pdf import PdfExtractionError, extract_pdf_text

logger = logging.getLogger(__name__)


def extract_uploaded_document(uploaded_file: object, document: UploadedDocument) -> ExtractedDocument:
    logger.info("Reading uploaded file bytes for %s.", document.filename)
    file_bytes = _read_uploaded_file(uploaded_file)
    return extract_pdf_text(file_bytes, document.filename, document.role)


def _read_uploaded_file(uploaded_file: object) -> bytes:
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    file_bytes = uploaded_file.read()
    if not isinstance(file_bytes, bytes):
        logger.warning("Uploaded file object did not return bytes.")
        raise PdfExtractionError("The uploaded file could not be read from the browser session.")

    return file_bytes
