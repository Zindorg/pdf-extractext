"""Tests para validate_filename - filename vacio."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_utils import validate_filename


class TestValidateFilenameEmpty:
    """Rechaza filename vacio."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            validate_filename("")
