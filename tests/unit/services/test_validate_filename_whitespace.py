"""Tests para validate_filename - solo espacios."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_utils import validate_filename


class TestValidateFilenameWhitespace:
    """Rechaza filename solo con espacios."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            validate_filename("   ")
