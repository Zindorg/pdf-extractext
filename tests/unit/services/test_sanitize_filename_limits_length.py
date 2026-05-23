"""Tests para sanitize_filename - limita longitud."""

from app.services.pdf_utils import sanitize_filename


class TestSanitizeFilenameLimitsLength:
    """Limita a 50 caracteres."""

    def test_limits_to_50_chars(self):
        long_name = "a" * 100 + ".pdf"
        assert len(sanitize_filename(long_name)) <= 50
