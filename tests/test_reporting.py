from __future__ import annotations

import unittest

from app.models.analysis import AnalysisResult, Finding
from app.services.reporting import build_scorecard_metrics


class ScorecardMetricsTests(unittest.TestCase):
    def test_build_scorecard_metrics_counts_findings_and_highest_severity(self) -> None:
        result = AnalysisResult(
            summary="summary",
            gaps=[
                Finding(
                    category="gaps",
                    severity="High",
                    title="Gap",
                    description="desc",
                    evidence="evidence",
                    recommendation="rec",
                )
            ],
            inconsistencies=[
                Finding(
                    category="inconsistencies",
                    severity="Medium",
                    title="Mismatch",
                    description="desc",
                    evidence="evidence",
                    recommendation="rec",
                )
            ],
            risks=[
                Finding(
                    category="risks",
                    severity="Critical",
                    title="Risk",
                    description="desc",
                    evidence="evidence",
                    recommendation="rec",
                )
            ],
            recommendations=[],
        )

        metrics = build_scorecard_metrics(result)

        self.assertEqual(metrics.total_findings, 3)
        self.assertEqual(metrics.highest_severity, "Critical")
        self.assertEqual(metrics.severity_counts["Critical"], 1)
        self.assertEqual(metrics.severity_counts["High"], 1)
        self.assertEqual(metrics.categories_with_findings, 3)

    def test_build_scorecard_metrics_handles_no_findings(self) -> None:
        metrics = build_scorecard_metrics(AnalysisResult(summary=""))

        self.assertEqual(metrics.total_findings, 0)
        self.assertIsNone(metrics.highest_severity)
        self.assertEqual(metrics.categories_with_findings, 0)
        self.assertEqual(sum(metrics.severity_counts.values()), 0)


if __name__ == "__main__":
    unittest.main()
