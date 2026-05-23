"""Tests para el caso de uso ExtractText."""

from unittest.mock import MagicMock

import pytest

from app.models.pdf_document import PDFDocument
from datetime import datetime
from app.exceptions import PDFNotFoundException
from app.use_cases.extract_text import ExtractText


class TestExtractText:
    """Extraer texto de PDF existente."""

    def test_returns_text(self):

        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="Extracted text",
            page_count=5,
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_queries = MagicMock()
        mock_queries.get_persisted_document.return_value = doc

        use_case = ExtractText(mock_queries)
        result = use_case.execute("507f1f77bcf86cd799439011")

        assert result.text == "Extracted text"
        assert result.pages_extracted == 5
    
    """Extraer texto de PDF inexistente lanza exception."""

    def test_raises_exception(self):
        mock_queries = MagicMock()
        mock_queries.get_persisted_document.side_effect = PDFNotFoundException("Not found")

        use_case = ExtractText(mock_queries)
        with pytest.raises(PDFNotFoundException):
            use_case.execute("nonexistent")
