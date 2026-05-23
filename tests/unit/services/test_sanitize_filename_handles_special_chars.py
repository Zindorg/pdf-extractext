"""Tests para sanitize_filename - sanitiza caracteres especiales."""

from app.services.pdf_utils import sanitize_filename


class TestSanitizeFilenameHandlesSpecialChars:
    """Sanitiza caracteres especiales."""

    def test_sanitizes_special_chars(self):
        result = sanitize_filename("!@#$.pdf")
        assert not any(ch in result for ch in "!@#$")
