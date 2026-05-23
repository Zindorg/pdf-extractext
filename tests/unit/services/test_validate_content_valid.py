"""Tests para validate_content - contenido valido."""

from app.services.pdf_utils import validate_content


class TestValidateContentValid:
    """Acepta contenido valido."""

    def test_accepts_valid(self):
        assert validate_content(b"some content") is None
