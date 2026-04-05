from __future__ import annotations

import unittest

from app.models.documents import ExtractedDocument, ExtractedPage
from app.services.chunking import chunk_extracted_document


class ChunkingBehaviorTests(unittest.TestCase):
    def test_chunking_creates_deterministic_chunks_with_metadata(self) -> None:
        page_one = ExtractedPage(
            page_number=1,
            text=(
                "1. Purpose\n\nThis policy defines remote work expectations and device controls. "
                "It also sets minimum management review duties.\n\n"
                "2. Scope\n\nThis policy applies to employees and contractors using company systems."
            ),
            character_count=0,
        )
        page_two = ExtractedPage(
            page_number=2,
            text=(
                "3. Controls\n\nAll laptops must use disk encryption. Access rights must be reviewed "
                "quarterly and exceptions must be approved by management."
            ),
            character_count=0,
        )
        document = ExtractedDocument(
            filename="policy.pdf",
            role="primary",
            page_count=2,
            extracted_character_count=len(page_one.text) + len(page_two.text),
            text=f"{page_one.text}\n\n{page_two.text}",
            pages=[page_one, page_two],
            warnings=[],
        )

        result = chunk_extracted_document(document, chunk_size=170, chunk_overlap=40)

        self.assertEqual(result.chunk_count, 3)
        self.assertEqual(result.chunks[0].chunk_id, "primary-001")
        self.assertEqual(result.chunks[0].section_heading, "1. Purpose")
        self.assertEqual(result.chunks[0].start_page, 1)
        self.assertEqual(result.chunks[1].section_heading, "2. Scope")
        self.assertEqual(result.chunks[2].end_page, 2)

    def test_chunking_rejects_invalid_overlap(self) -> None:
        document = ExtractedDocument(
            filename="policy.pdf",
            role="primary",
            page_count=1,
            extracted_character_count=100,
            text="Simple policy text.",
            pages=[ExtractedPage(page_number=1, text="Simple policy text.", character_count=19)],
            warnings=[],
        )

        with self.assertRaises(ValueError):
            chunk_extracted_document(document, chunk_size=100, chunk_overlap=100)


if __name__ == "__main__":
    unittest.main()
