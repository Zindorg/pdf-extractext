"""Tests para _validate_content - contenido vacio."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_content


class TestValidateContentEmpty:
    """Rechaza contenido vacio."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_content(b"")
