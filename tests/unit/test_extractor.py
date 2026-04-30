"""Unit tests for PDF text extraction."""

from pathlib import Path

from app.infrastructure import pdf_extractor


def get_fixture_bytes(filename: str) -> bytes:
    """Load PDF fixture as bytes."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / filename
    return fixture_path.read_bytes()


class TestExtractText:
    """Tests for extract_text function."""

    def test_returns_string_and_page_count_from_valid_pdf(self):
        """Should return extracted text and page count from a valid PDF."""
        content = get_fixture_bytes("valid.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert isinstance(result, str)
        assert isinstance(page_count, int)
        assert page_count >= 0

    def test_returns_empty_string_for_empty_pdf(self):
        """Should return empty string when PDF has no content."""
        content = get_fixture_bytes("empty.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert result == ""
        assert page_count == 0


class TestExtractTextFromPageRange:
    """Tests for extract_text_from_page_range function."""

    def test_extracts_text_from_specific_page_range(self):
        """Should extract text from specific page range."""
        content = get_fixture_bytes("multipage.pdf")
        result, pages_extracted = pdf_extractor.extract_text_from_page_range(
            content, start_page=2, end_page=4
        )

        assert pages_extracted == 3


class TestUnicodeContent:
    """Tests for unicode content handling."""

    def test_extracts_unicode_content(self):
        """Should extract unicode content without errors."""
        content = get_fixture_bytes("unicode.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert isinstance(result, str)
        assert page_count >= 1
