"""Tests para GET /pdfs/{doc_id}/download."""

from datetime import datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.exceptions import PDFNotFoundException
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
        mock_queries = MagicMock()
        mock_queries.get_persisted_document.return_value = doc

        client = TestClient(_create_test_app(mock_queries=mock_queries))
        resp = client.get("/pdfs/507f1f77bcf86cd799439011/download")

        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/plain; charset=utf-8"
        assert b"Extracted text content" in resp.content

    """Descargar texto de PDF inexistente retorna 404."""

    def test_returns_404(self):
        mock_queries = MagicMock()
        mock_queries.get_persisted_document.return_value = None

        client = TestClient(_create_test_app(mock_queries=mock_queries))
        resp = client.get("/pdfs/nonexistent/download")

        assert resp.status_code == 404
        body = resp.json()
        assert body["title"] == "Not Found"
        assert body["status"] == 404


class TestDownloadFilename:
    """El nombre del .txt se deriva del PDF sin romper la cabecera HTTP."""

    def _download(self, filename):
        from unittest.mock import MagicMock

        from fastapi.testclient import TestClient

        from tests.unit.api.utils import _create_test_app, _make_document

        queries = MagicMock()
        queries.get_persisted_document.return_value = _make_document(filename=filename)
        client = TestClient(_create_test_app(mock_queries=queries))
        return client.get("/pdfs/507f1f77bcf86cd799439011/download")

    def test_uppercase_extension_is_replaced(self):
        resp = self._download("INFORME.PDF")
        assert 'filename="INFORME.txt"' in resp.headers["content-disposition"]

    def test_only_the_extension_is_replaced(self):
        resp = self._download("mi.pdf.backup.pdf")
        assert 'filename="mi.pdf.backup.txt"' in resp.headers["content-disposition"]

    def test_quotes_and_non_ascii_are_escaped(self):
        resp = self._download('año "final".pdf')
        header = resp.headers["content-disposition"]
        assert 'filename="a_o _final_.txt"' in header
        assert "filename*=UTF-8''a%C3%B1o%20%22final%22.txt" in header