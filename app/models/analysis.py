from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SeverityLevel = Literal["Critical", "High", "Medium", "Low"]
VALID_SEVERITIES: tuple[SeverityLevel, ...] = ("Critical", "High", "Medium", "Low")
MAX_FINDINGS_PER_CATEGORY = 8


def _normalize_summary(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


def _normalize_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


@dataclass(slots=True)
class Finding:
    category: str
    severity: SeverityLevel
    title: str
    description: str
    evidence: str
    recommendation: str


@dataclass(slots=True)
class ChunkAnalysis:
    chunk_id: str
    summary: str = ""
    gaps: list[Finding] = field(default_factory=list)
    inconsistencies: list[Finding] = field(default_factory=list)
    risks: list[Finding] = field(default_factory=list)
    recommendations: list[Finding] = field(default_factory=list)

    @classmethod
    def from_payload(cls, chunk_id: str, payload: dict[str, object]) -> "ChunkAnalysis":
        return cls(
            chunk_id=chunk_id,
            summary=_normalize_summary(payload.get("summary")),
            gaps=_normalize_findings(payload.get("gaps"), "gaps"),
            inconsistencies=_normalize_findings(payload.get("inconsistencies"), "inconsistencies"),
            risks=_normalize_findings(payload.get("risks"), "risks"),
            recommendations=_normalize_findings(payload.get("recommendations"), "recommendations"),
        )


@dataclass(slots=True)
class AnalysisResult:
    summary: str = ""
    gaps: list[Finding] = field(default_factory=list)
    inconsistencies: list[Finding] = field(default_factory=list)
    risks: list[Finding] = field(default_factory=list)
    recommendations: list[Finding] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "AnalysisResult":
        return cls(
            summary=_normalize_summary(payload.get("summary")),
            gaps=_normalize_findings(payload.get("gaps"), "gaps"),
            inconsistencies=_normalize_findings(payload.get("inconsistencies"), "inconsistencies"),
            risks=_normalize_findings(payload.get("risks"), "risks"),
            recommendations=_normalize_findings(payload.get("recommendations"), "recommendations"),
        )


@dataclass(slots=True)
class AnalysisRequest:
    primary_document_name: str
    reference_document_name: str | None = None
    primary_chunk_count: int = 0
    reference_chunk_count: int = 0


def _normalize_findings(value: object, category: str) -> list[Finding]:
    if not isinstance(value, list):
        return []

    normalized_findings: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()

    for item in value:
        finding = _normalize_finding(item, category)
        if not finding:
            continue

        dedupe_key = (
            finding.severity,
            finding.title.lower(),
            finding.description.lower(),
        )
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        normalized_findings.append(finding)

        if len(normalized_findings) >= MAX_FINDINGS_PER_CATEGORY:
            break

    return normalized_findings


def _normalize_finding(value: object, category: str) -> Finding | None:
    if isinstance(value, str):
        fallback = _normalize_text(value)
        if not fallback:
            return None
        return Finding(
            category=category,
            severity="Medium",
            title=fallback,
            description=fallback,
            evidence="Evidence not provided.",
            recommendation="No recommendation provided.",
        )

    if not isinstance(value, dict):
        return None

    severity = _normalize_severity(value.get("severity"))
    title = _normalize_text(value.get("title"))
    description = _normalize_text(value.get("description"))
    evidence = _normalize_text(value.get("evidence"))
    recommendation = _normalize_text(value.get("recommendation"))

    if not title:
        title = description
    if not description:
        description = title
    if not title and not description:
        return None

    if not evidence:
        evidence = "Evidence not provided."
    if not recommendation:
        recommendation = "No recommendation provided."

    return Finding(
        category=category,
        severity=severity,
        title=title,
        description=description,
        evidence=evidence,
        recommendation=recommendation,
    )


def _normalize_severity(value: object) -> SeverityLevel:
    if not isinstance(value, str):
        return "Medium"

    normalized = value.strip().lower()
    severity_map: dict[str, SeverityLevel] = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }
    return severity_map.get(normalized, "Medium")
