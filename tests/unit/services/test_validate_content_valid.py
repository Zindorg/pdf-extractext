"""Tests para _validate_content - contenido valido."""

from app.services.pdf_service import _validate_content


class TestValidateContentValid:
    """Acepta contenido valido."""

    def test_accepts_valid(self):
        assert _validate_content(b"some content") is None
