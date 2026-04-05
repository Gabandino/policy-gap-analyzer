from __future__ import annotations

import unittest

from app.models.analysis import AnalysisRequest, AnalysisResult, Finding
from app.services.export import build_analysis_pdf_report


class ExportPdfTests(unittest.TestCase):
    def test_build_analysis_pdf_report_returns_pdf_bytes(self) -> None:
        request = AnalysisRequest(primary_document_name="policy.pdf")
        result = AnalysisResult(
            summary="Short summary",
            gaps=[
                Finding(
                    category="gaps",
                    severity="High",
                    title="Missing owner",
                    description="No owner is assigned.",
                    evidence="chunk-1 page 2",
                    recommendation="Assign a policy owner.",
                )
            ],
        )

        pdf_bytes = build_analysis_pdf_report(
            analysis_request=request,
            analysis_result=result,
        )

        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"Policy Gap Analyzer Report", pdf_bytes)
        self.assertIn(b"Missing owner", pdf_bytes)


if __name__ == "__main__":
    unittest.main()
