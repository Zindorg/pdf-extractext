"""Tests para POST /pdfs - upload valido."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from tests.unit.api.utils import _create_test_app, _make_document


class TestUploadValidPdf:
    """Subir PDF valido retorna 200 con datos."""

    def test_returns_200_with_data(self):
        doc = _make_document()
        mock_svc = MagicMock()
        mock_svc.generate_checksum.return_value = "checksum123"
        mock_svc.find_by_checksum.return_value = None
        mock_svc.process_pdf = AsyncMock(return_value=doc)

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
