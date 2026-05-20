"""Tests para GET /pdfs/{doc_id}/download."""

from datetime import datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.models.pdf_document import PDFDocument
from tests.unit.api.utils import _create_test_app


class TestDownloadText:
    """Descargar texto de PDF existente retorna 200 con stream."""

    def test_returns_200_with_text_stream(self):
        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="Extracted text content",
            page_count=5,
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_svc = MagicMock()
        mock_svc.get_persisted_document.return_value = doc

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs/507f1f77bcf86cd799439011/download")

        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/plain; charset=utf-8"
        assert b"Extracted text content" in resp.content

    """Descargar texto de PDF inexistente retorna 404."""

    def test_returns_404(self):
        mock_svc = MagicMock()
        mock_svc.get_persisted_document.return_value = None

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs/nonexistent/download")

        assert resp.status_code == 404
        body = resp.json()
        assert body["title"] == "Not Found"
        assert body["status"] == 404
