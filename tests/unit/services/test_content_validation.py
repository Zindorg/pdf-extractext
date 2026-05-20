"""Tests para validacion de contenido."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_content


class TestContentValidation:
    """Rechaza contenido vacio."""

    def test_raises_exception(self):
        with pytest.raises(InvalidFileException):
            _validate_content(b"")
    
    def test_accepts_valid(self):
        assert _validate_content(b"some content") is None
