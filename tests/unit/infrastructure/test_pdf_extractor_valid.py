"""Tests para extracción de texto PDF valido."""
from app.infrastructure import pdf_extractor
from tests.unit.infrastructure._fixture_bytes import _fixture_bytes


class TestExtractText:
    """Extraer texto retorna string y conteo de paginas."""

    def test_returns_string_and_count(self):
        content = _fixture_bytes("valid.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert isinstance(result, str)
        assert isinstance(page_count, int)
        assert page_count >= 0
    
    """Extraer texto de PDF vacio retorna string vacio."""

    def test_returns_empty(self):
        content = _fixture_bytes("empty.pdf")
        result, page_count = pdf_extractor.extract_text(content)

        assert result == ""
        assert page_count == 0
