from __future__ import annotations

from dataclasses import dataclass

from app.models.analysis import AnalysisResult, Finding, SeverityLevel

SEVERITY_ORDER: tuple[SeverityLevel, ...] = ("Critical", "High", "Medium", "Low")


@dataclass(slots=True)
class ScorecardMetrics:
    total_findings: int
    highest_severity: SeverityLevel | None
    severity_counts: dict[SeverityLevel, int]
    categories_with_findings: int


def build_scorecard_metrics(result: AnalysisResult) -> ScorecardMetrics:
    all_findings = _all_findings(result)
    severity_counts: dict[SeverityLevel, int] = {level: 0 for level in SEVERITY_ORDER}

    for finding in all_findings:
        severity_counts[finding.severity] += 1

    highest_severity = next(
        (level for level in SEVERITY_ORDER if severity_counts[level] > 0),
        None,
    )

    categories_with_findings = sum(
        1
        for category_findings in (
            result.gaps,
            result.inconsistencies,
            result.risks,
            result.recommendations,
        )
        if category_findings
    )

    return ScorecardMetrics(
        total_findings=len(all_findings),
        highest_severity=highest_severity,
        severity_counts=severity_counts,
        categories_with_findings=categories_with_findings,
    )


def _all_findings(result: AnalysisResult) -> list[Finding]:
    return result.gaps + result.inconsistencies + result.risks + result.recommendations
