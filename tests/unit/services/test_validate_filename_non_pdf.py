"""Tests para _validate_filename - extension no PDF."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_filename


class TestValidateFilenameNonPdf:
    """Rechaza extensiones no-PDF."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("document.txt")
