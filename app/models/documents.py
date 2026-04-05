from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class UploadedDocument:
    filename: str
    content_type: str | None
    size_bytes: int
    role: str

    @property
    def extension(self) -> str:
        if "." not in self.filename:
            return ""
        return self.filename.rsplit(".", maxsplit=1)[-1].lower()


@dataclass(slots=True)
class ExtractedPage:
    page_number: int
    text: str
    character_count: int


@dataclass(slots=True)
class ExtractedDocument:
    filename: str
    role: str
    page_count: int
    extracted_character_count: int
    text: str
    pages: list[ExtractedPage] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DocumentChunk:
    chunk_id: str
    source_document_label: str
    text: str
    start_page: int | None = None
    end_page: int | None = None
    section_heading: str | None = None

    @property
    def character_count(self) -> int:
        return len(self.text)


@dataclass(slots=True)
class ChunkingResult:
    filename: str
    role: str
    source_document_label: str
    chunks: list[DocumentChunk] = field(default_factory=list)
    discarded_chunk_count: int = 0

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)
