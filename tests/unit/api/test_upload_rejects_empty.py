"""Tests para POST /pdfs - rechazar archivo vacio."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.exceptions import InvalidFileException
from tests.unit.api.utils import _create_test_app


class TestUploadRejectsEmptyFile:
    """Subir archivo vacio retorna 422."""

    def test_rejects_empty_file(self):
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(side_effect=InvalidFileException("File is empty"))

        client = TestClient(_create_test_app(mock_extraction=mock_extraction))
        resp = client.post(
            "/pdfs",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert resp.status_code == 422
        body = resp.json()
        assert body["title"] == "Unprocessable Entity"
        assert body["status"] == 422
