"""Tests para extracción de rango de paginas PDF."""

from app.infrastructure import pdf_extractor

from tests.unit.infrastructure._fixture_bytes import _fixture_bytes


class TestExtractTextFromPageRange:
    """Extraer texto de rango de paginas especifico."""

    def test_extracts_from_range(self):
        content = _fixture_bytes("multipage.pdf")
        result, pages_extracted = pdf_extractor.extract_text_from_page_range(
            content, start_page=2, end_page=4
        )
        assert pages_extracted == 3
