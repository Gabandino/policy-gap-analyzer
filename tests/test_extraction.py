from __future__ import annotations

import unittest

from app.parsers.pdf import normalize_extracted_text


class ExtractionNormalizationTests(unittest.TestCase):
    def test_normalize_extracted_text_collapses_whitespace_and_preserves_paragraphs(self) -> None:
        raw_text = "Policy   Overview\r\nLine two\t\twith spacing\r\n\r\n\r\nNext   paragraph"

        normalized = normalize_extracted_text(raw_text)

        self.assertEqual(normalized, "Policy Overview Line two with spacing\n\nNext paragraph")

    def test_normalize_extracted_text_removes_empty_content(self) -> None:
        self.assertEqual(normalize_extracted_text(" \r\n\t\r\n "), "")


if __name__ == "__main__":
    unittest.main()
