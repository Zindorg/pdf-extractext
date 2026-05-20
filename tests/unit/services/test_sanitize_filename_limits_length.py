"""Tests para _sanitize_filename - limita longitud."""

from app.services.pdf_service import _sanitize_filename


class TestSanitizeFilenameLimitsLength:
    """Limita a 50 caracteres."""

    def test_limits_to_50_chars(self):
        long_name = "a" * 100 + ".pdf"
        assert len(_sanitize_filename(long_name)) <= 50
