"""Tests para _validate_filename - filename valido."""

from app.services.pdf_service import _validate_filename


class TestValidateFilenameValid:
    """Acepta filename valido."""

    def test_accepts_valid(self):
        assert _validate_filename("document.pdf") is None
