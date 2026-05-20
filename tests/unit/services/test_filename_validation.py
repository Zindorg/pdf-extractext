"""Tests para validacion de filename."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_filename


class TestFilenameValidation:
    """Rechaza filename vacio."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("")

    """Rechaza filename solo con espacios."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("   ")

    """Rechaza extensiones no-PDF."""

    @pytest.mark.parametrize(
        "filename",
        [
            "document.txt",
            "document.doc",
            "document.docx",
            "image.png",
            "image.jpg",
            "document",
        ],
    )
    def test_raises_exception(self, filename):
        with pytest.raises(InvalidFileException):
            _validate_filename(filename)

    """Acepta PDF en cualquier case."""

    @pytest.mark.parametrize(
        "filename", ["document.pdf", "document.PDF", "document.Pdf", "document.pDf"]
    )
    def test_accepts_any_case(self, filename):
        assert _validate_filename(filename) is None

    """Acepta path con extension PDF."""

    def test_accepts_path_with_pdf(self):
        assert _validate_filename("path/to/document.pdf") is None
