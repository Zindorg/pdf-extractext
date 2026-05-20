"""Tests para GET /pdfs (list)."""

from datetime import datetime
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.models.pdf_document import PDFDocument
from tests.unit.api.utils import _create_test_app, _make_document

class TestList:
    """Listar sin documentos retorna lista vacia."""

    def test_returns_empty_list(self):
        mock_svc = MagicMock()
        mock_svc.find_all.return_value = []

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs")

        assert resp.status_code == 200
        body = resp.json()
        assert body["documents"] == []
        assert body["total"] == 0
    
    """Listar documentos existentes."""

    def test_returns_all_documents(self):
        docs = [
            _make_document(id="id1", filename="a.pdf", checksum="c1"),
            _make_document(id="id2", filename="b.pdf", checksum="c2"),
        ]
        mock_svc = MagicMock()
        mock_svc.find_all.return_value = docs

        client = TestClient(_create_test_app(mock_svc))
        resp = client.get("/pdfs")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        filenames = [d["filename"] for d in body["documents"]]
        assert "a.pdf" in filenames
        assert "b.pdf" in filenames
