"""Tests para validate_filename - extension no PDF."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_utils import validate_filename


class TestValidateFilenameNonPdf:
    """Rechaza extensiones no-PDF."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            validate_filename("document.txt")
