"""Tests para _validate_filename - filename vacio."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_filename


class TestValidateFilenameEmpty:
    """Rechaza filename vacio."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("")
