"""Tests para la extracción de texto PDF."""

from pathlib import Path

import pytest

from app.infrastructure import pdf_extractor


def _fixture_bytes(filename: str) -> bytes:
    """Carga un fixture PDF como bytes."""
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / filename
    return fixture_path.read_bytes()


class TestExtractText:
    def test_returns_string_and_page_count_from_valid_pdf(self):
        content = _fixture_bytes("valid.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert isinstance(result, str)
        assert isinstance(page_count, int)
        assert page_count >= 0

    def test_returns_empty_string_for_empty_pdf(self):
        content = _fixture_bytes("empty.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert result == ""
        assert page_count == 0


class TestExtractTextFromPageRange:
    def test_extracts_text_from_specific_page_range(self):
        content = _fixture_bytes("multipage.pdf")
        result, pages_extracted = pdf_extractor.extract_text_from_page_range(
            content, start_page=2, end_page=4
        )
        assert pages_extracted == 3


class TestUnicodeContent:
    def test_extracts_unicode_content(self):
        content = _fixture_bytes("unicode.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert isinstance(result, str)
        assert page_count >= 1
