"""Tests para POST /pdfs - rechazar no-PDF."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.exceptions import InvalidFileException
from tests.unit.api.utils import _create_test_app


class TestUploadRejectsNonPdf:
    """Subir archivo no-PDF retorna 422."""

    def test_rejects_non_pdf_content_type(self):
        mock_svc = MagicMock()
        mock_svc.process_upload = AsyncMock(side_effect=InvalidFileException("File must be a PDF"))

        client = TestClient(_create_test_app(mock_svc))
        resp = client.post(
            "/pdfs",
            files={"file": ("image.png", b"png data", "image/png")},
        )
        assert resp.status_code == 422
        body = resp.json()
        assert body["title"] == "Unprocessable Entity"
        assert body["status"] == 422
