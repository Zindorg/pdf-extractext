"""Tests para validate_filename - filename valido."""

from app.services.pdf_utils import validate_filename


class TestValidateFilenameValid:
    """Acepta filename valido."""

    def test_accepts_valid(self):
        assert validate_filename("document.pdf") is None
