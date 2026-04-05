from __future__ import annotations

from dataclasses import dataclass, field


def _normalize_summary(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


def _normalize_items(value: object, limit: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized_items: list[str] = []
    seen: set[str] = set()

    for item in value:
        if not isinstance(item, str):
            continue

        cleaned_item = " ".join(item.split()).strip()
        if not cleaned_item:
            continue
        if cleaned_item in seen:
            continue

        seen.add(cleaned_item)
        normalized_items.append(cleaned_item)

        if len(normalized_items) >= limit:
            break

    return normalized_items


@dataclass(slots=True)
class ChunkAnalysis:
    chunk_id: str
    summary: str = ""
    gaps: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @classmethod
    def from_payload(cls, chunk_id: str, payload: dict[str, object]) -> "ChunkAnalysis":
        return cls(
            chunk_id=chunk_id,
            summary=_normalize_summary(payload.get("summary")),
            gaps=_normalize_items(payload.get("gaps")),
            inconsistencies=_normalize_items(payload.get("inconsistencies")),
            risks=_normalize_items(payload.get("risks")),
            recommendations=_normalize_items(payload.get("recommendations")),
        )


@dataclass(slots=True)
class AnalysisResult:
    summary: str = ""
    gaps: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "AnalysisResult":
        return cls(
            summary=_normalize_summary(payload.get("summary")),
            gaps=_normalize_items(payload.get("gaps")),
            inconsistencies=_normalize_items(payload.get("inconsistencies")),
            risks=_normalize_items(payload.get("risks")),
            recommendations=_normalize_items(payload.get("recommendations")),
        )


@dataclass(slots=True)
class AnalysisRequest:
    primary_document_name: str
    reference_document_name: str | None = None
    primary_chunk_count: int = 0
    reference_chunk_count: int = 0
