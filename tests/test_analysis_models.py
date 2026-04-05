from __future__ import annotations

import unittest

from app.models.analysis import AnalysisResult, ChunkAnalysis


class AnalysisSchemaHandlingTests(unittest.TestCase):
    def test_analysis_result_normalizes_and_limits_items(self) -> None:
        payload = {
            "summary": "  A concise   summary of findings. ",
            "gaps": [" Missing access review cadence ", "Missing access review cadence", "", 3],
            "inconsistencies": [" Statement A conflicts with statement B "],
            "risks": ["Weak access control language"] * 8,
            "recommendations": [" Add quarterly reviews ", "Add quarterly reviews", "Add MFA"],
        }

        result = AnalysisResult.from_payload(payload)

        self.assertEqual(result.summary, "A concise summary of findings.")
        self.assertEqual(result.gaps, ["Missing access review cadence"])
        self.assertEqual(result.inconsistencies, ["Statement A conflicts with statement B"])
        self.assertEqual(result.risks, ["Weak access control language"])
        self.assertEqual(result.recommendations, ["Add quarterly reviews", "Add MFA"])

    def test_chunk_analysis_from_payload_ignores_invalid_shapes(self) -> None:
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
        self.assertEqual(result.risks, ["vague ownership"])
        self.assertEqual(result.recommendations, ["Clarify responsibilities"])


if __name__ == "__main__":
    unittest.main()
