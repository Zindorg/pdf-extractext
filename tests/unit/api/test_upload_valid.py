"""Tests para POST /pdfs - upload valido."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from tests.unit.api.utils import _create_test_app, _make_document


class TestUploadValidPdf:
    """Subir PDF valido retorna 200 con datos."""

    def test_returns_200_with_data(self):
        mock_svc = MagicMock()
        mock_svc.process_upload = AsyncMock(return_value={
            "id": "507f1f77bcf86cd799439011",
            "filename": "document.pdf",
            "page_count": 5,
            "file_size": 1024,
            "text_preview": "Extracted text",
            "checksum": "abc123checksum",
            "is_duplicate": False,
        })

        client = TestClient(_create_test_app(mock_svc))
        resp = client.post(
            "/pdfs",
            files={"file": ("doc.pdf", b"%pdf content", "application/pdf")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["filename"] == "document.pdf"
        assert body["id"] == "507f1f77bcf86cd799439011"
        assert body["is_duplicate"] is False
        assert body["checksum"] == "abc123checksum"
