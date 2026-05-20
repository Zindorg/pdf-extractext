"""Tests para extracción de texto unicode PDF."""

from tests.unit.infrastructure._fixture_bytes import _fixture_bytes

from app.infrastructure import pdf_extractor

class TestExtractTextUnicode:
    """Extraer texto unicode de PDF."""

    def test_extracts_unicode(self):
        content = _fixture_bytes("unicode.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert isinstance(result, str)
        assert page_count >= 1
