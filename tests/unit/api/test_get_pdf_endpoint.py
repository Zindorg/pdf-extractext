"""Tests para GET /pdfs/{doc_id}."""

from unittest.mock import MagicMock 
from fastapi.testclient import TestClient

from tests.unit.api.utils import _create_test_app, _make_document

class TestGet:
    """Obtener PDF existente retorna detalle completo."""

    def test_returns_full_detail(self):
        doc = _make_document(text_content="Full document text here")
        mock_svc = MagicMock()
        mock_svc.find_by_id.return_value = doc

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs/507f1f77bcf86cd799439011")

        assert resp.status_code == 200
        body = resp.json()
        assert body["text_content"] == "Full document text here"
        assert body["filename"] == "document.pdf"
    
    """Obtener PDF inexistente retorna 404."""

    def test_returns_404(self):
        mock_svc = MagicMock()
        mock_svc.find_by_id.return_value = None

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs/nonexistent-id")

        assert resp.status_code == 404
