"""Tests para el caso de uso GetPDF."""

from unittest.mock import MagicMock

from app.use_cases.get_pdf import GetPDF
from app.models.pdf_document import PDFDocument
from datetime import datetime

class TestGetPdf:
    """Obtener PDF existente."""

    def test_returns_pdf(self):
        
        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="content",
            page_count=5,
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_queries = MagicMock()
        mock_queries.find_by_id.return_value = doc

        use_case = GetPDF(mock_queries)
        result = use_case.execute("507f1f77bcf86cd799439011")

        assert result is not None
        assert result.filename == "test.pdf"

    """Obtener PDF inexistente."""

    def test_returns_none(self):
        mock_queries = MagicMock()
        mock_queries.find_by_id.return_value = None

        use_case = GetPDF(mock_queries)
        result = use_case.execute("nonexistent")

        assert result is None
