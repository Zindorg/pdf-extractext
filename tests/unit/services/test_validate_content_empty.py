"""Tests para validate_content - contenido vacio."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_utils import validate_content


class TestValidateContentEmpty:
    """Rechaza contenido vacio."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            validate_content(b"")
