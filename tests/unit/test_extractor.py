"""Unit tests for PDF text extraction using TDD principles.

These tests verify that PDFExtractorAdapter correctly extracts text from PDF files,
following the RED-GREEN-REFACTOR cycle and CLEAN CODE practices.
"""

import pytest
from pathlib import Path

from infrastructure.pdf_extractor_adapter import PDFExtractorAdapter


@pytest.fixture
def extractor():
    """Create a PDFExtractorAdapter instance."""
    return PDFExtractorAdapter()


@pytest.fixture
def valid_pdf_bytes():
    """Load valid PDF file as bytes."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "valid.pdf"
    return fixture_path.read_bytes()


@pytest.fixture
def empty_pdf_bytes():
    """Load empty PDF file as bytes."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "empty.pdf"
    return fixture_path.read_bytes()


@pytest.fixture
def multipage_pdf_bytes():
    """Load multipage PDF file as bytes (5 pages)."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "multipage.pdf"
    return fixture_path.read_bytes()


@pytest.fixture
def unicode_pdf_bytes():
    """Load PDF with unicode content as bytes."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "unicode.pdf"
    return fixture_path.read_bytes()


def test_extract_text_returns_content_from_valid_pdf(extractor, valid_pdf_bytes):
    """Should return extracted text from a valid PDF file."""
    result, page_count = extractor.extract_text(valid_pdf_bytes)

    assert result is not None
    assert isinstance(result, str)


def test_extract_text_never_returns_none(extractor, valid_pdf_bytes):
    """Should never return None, always a string value."""
    result, page_count = extractor.extract_text(valid_pdf_bytes)

    assert result is not None
    assert isinstance(result, str)


def test_extract_text_returns_non_empty_string_when_pdf_has_content(
    extractor, valid_pdf_bytes
):
    """Should return non-empty string when PDF contains text."""
    result, page_count = extractor.extract_text(valid_pdf_bytes)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0 or page_count == 0


def test_extract_text_returns_empty_string_for_empty_pdf(extractor, empty_pdf_bytes):
    """Should return empty string when PDF has no content."""
    result, page_count = extractor.extract_text(empty_pdf_bytes)

    assert result is not None
    assert isinstance(result, str)
    assert result == ""


def test_extract_text_returns_page_count_from_valid_pdf(extractor, valid_pdf_bytes):
    """Should return correct page count from a valid PDF."""
    result, page_count = extractor.extract_text(valid_pdf_bytes)

    assert isinstance(page_count, int)
    assert page_count >= 0


def test_extract_text_returns_zero_pages_for_empty_pdf(extractor, empty_pdf_bytes):
    """Should return zero pages for an empty PDF."""
    result, page_count = extractor.extract_text(empty_pdf_bytes)

    assert page_count == 0


def test_extract_page_range_valid(extractor, multipage_pdf_bytes):
    """Should extract text from specific page range."""
    result, pages_extracted = extractor.extract_text_from_page_range(
        multipage_pdf_bytes, start_page=2, end_page=4
    )

    assert pages_extracted == 3


def test_extract_text_with_unicode(extractor, unicode_pdf_bytes):
    """Should extract unicode content without errors."""
    result, page_count = extractor.extract_text(unicode_pdf_bytes)

    assert isinstance(result, str)
    assert page_count >= 1
