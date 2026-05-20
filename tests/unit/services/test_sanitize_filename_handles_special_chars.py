"""Tests para _sanitize_filename - sanitiza caracteres especiales."""

from app.services.pdf_service import _sanitize_filename


class TestSanitizeFilenameHandlesSpecialChars:
    """Sanitiza caracteres especiales."""

    def test_sanitizes_special_chars(self):
        result = _sanitize_filename("!@#$.pdf")
        assert not any(ch in result for ch in "!@#$")
