"""Tests para _validate_filename - solo espacios."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_filename


class TestValidateFilenameWhitespace:
    """Rechaza filename solo con espacios."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("   ")
