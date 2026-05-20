"""Tests para POST /pdfs/{file_id}/extract."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.exceptions import PDFNotFoundException
from tests.unit.api.utils import _create_test_app, _make_document

class TestExtract:
    """Extraer texto de PDF existente."""

    def test_returns_text(self):
        doc = _make_document()
        mock_svc = MagicMock()
        mock_svc.get_persisted_document = AsyncMock(return_value=doc)

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs/507f1f77bcf86cd799439011/text")

        assert resp.status_code == 200
        body = resp.json()
        assert body["text"] == "Extracted text"
        assert body["pages_extracted"] == 5
    
    """Extraer de PDF inexistente retorna 404."""

    def test_returns_404(self):
        mock_svc = MagicMock()
        mock_svc.get_persisted_document = AsyncMock(
            side_effect=PDFNotFoundException("Not found")
        )

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs/missing/text")

        assert resp.status_code == 404
