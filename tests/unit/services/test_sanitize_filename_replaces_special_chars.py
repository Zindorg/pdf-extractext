"""Tests para _sanitize_filename - reemplaza caracteres especiales."""

from app.services.pdf_service import _sanitize_filename


class TestSanitizeFilenameReplacesSpecialChars:
    """Reemplaza caracteres especiales."""

    def test_replaces_with_underscore(self):
        result = _sanitize_filename("doc & file [2024].pdf")
        assert not any(ch in result for ch in "&[]")
