"""Tests para POST /pdfs - upload valido."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.models.pdf_document import PDFDocument
from tests.unit.api.utils import _create_test_app


class TestUploadValidPdf:
    """Subir PDF valido retorna 200 con datos."""

    def test_returns_200_with_data(self):
        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123checksum",
            filename="document.pdf",
            page_count=5,
            file_size=1024,
            text_content="Extracted text",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(return_value=doc)

        client = TestClient(_create_test_app(mock_extraction=mock_extraction))
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
