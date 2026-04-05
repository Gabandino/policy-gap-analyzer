from __future__ import annotations

import unittest

from app.models.analysis import AnalysisResult, ChunkAnalysis


class AnalysisSchemaHandlingTests(unittest.TestCase):
    def test_analysis_result_normalizes_and_limits_findings(self) -> None:
        payload = {
            "summary": "  A concise   summary of findings. ",
            "gaps": [
                {
                    "category": "gaps",
                    "severity": "high",
                    "title": " Missing access review cadence ",
                    "description": " Missing quarterly access reviews ",
                    "evidence": "chunk-2 page 4: no review cadence listed",
                    "recommendation": "Add quarterly access review controls",
                },
                {
                    "category": "gaps",
                    "severity": "HIGH",
                    "title": "Missing access review cadence",
                    "description": "Missing quarterly access reviews",
                    "evidence": "duplicate",
                    "recommendation": "duplicate",
                },
            ],
            "inconsistencies": [
                {
                    "category": "inconsistencies",
                    "severity": "Medium",
                    "title": " Statement A conflicts with statement B ",
                    "description": " Statement A conflicts with statement B ",
                    "evidence": "chunk-5 page 7",
                    "recommendation": "Align retention statements",
                }
            ],
            "risks": [
                {
                    "category": "risks",
                    "severity": "Low",
                    "title": "Weak access control language",
                    "description": "Weak access control language",
                    "evidence": "chunk-3 page 2",
                    "recommendation": "Strengthen wording",
                }
            ]
            * 12,
            "recommendations": [
                {
                    "category": "recommendations",
                    "severity": "critical",
                    "title": " Add MFA ",
                    "description": "Enable MFA for all privileged accounts",
                    "evidence": "chunk-1 page 1",
                    "recommendation": "Roll out MFA in 30 days",
                }
            ],
        }

        result = AnalysisResult.from_payload(payload)

        self.assertEqual(result.summary, "A concise summary of findings.")
        self.assertEqual(len(result.gaps), 1)
        self.assertEqual(result.gaps[0].severity, "High")
        self.assertEqual(result.gaps[0].title, "Missing access review cadence")
        self.assertEqual(len(result.risks), 1)
        self.assertEqual(result.recommendations[0].severity, "Critical")

    def test_chunk_analysis_supports_legacy_string_findings(self) -> None:
        payload = {
            "summary": None,
            "gaps": "not-a-list",
            "inconsistencies": [],
            "risks": ["  vague ownership  "],
            "recommendations": [None, "Clarify responsibilities"],
        }

        result = ChunkAnalysis.from_payload("primary-001", payload)

        self.assertEqual(result.chunk_id, "primary-001")
        self.assertEqual(result.summary, "")
        self.assertEqual(result.gaps, [])
        self.assertEqual(result.risks[0].title, "vague ownership")
        self.assertEqual(result.risks[0].severity, "Medium")
        self.assertEqual(result.recommendations[0].title, "Clarify responsibilities")


if __name__ == "__main__":
    unittest.main()
