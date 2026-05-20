"""Tests para el caso de uso ListPDFs."""

from unittest.mock import MagicMock

from app.schemas.pdf_schemas import PDFListResponse
from app.use_cases.list_pdfs import ListPDFs
from app.models.pdf_document import PDFDocument
from datetime import datetime

class TestListPDFs:
    """Listado vacio retorna lista vacia."""

    def test_returns_empty_list(self):
        mock_service = MagicMock()
        mock_service.find_all.return_value = []

        use_case = ListPDFs(mock_service)
        result = use_case.execute()

        assert isinstance(result, PDFListResponse)
        assert result.documents == []
        assert result.total == 0

    """Listado con documentos."""

    def test_returns_all_documents(self):
        
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
        mock_service = MagicMock()
        mock_service.find_all.return_value = [doc]

        use_case = ListPDFs(mock_service)
        result = use_case.execute()

        assert isinstance(result, PDFListResponse)
        assert result.total == 1
        assert result.documents[0].filename == "test.pdf"
