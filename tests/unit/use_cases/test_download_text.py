"""Tests para el caso de uso DownloadExtractedText."""

from unittest.mock import MagicMock

import pytest

from app.exceptions import PDFNotFoundException
from app.use_cases.download_text import DownloadExtractedText


class TestDownloadText:
    """Descargar texto de PDF existente."""

    def test_returns_text(self):
        from app.models.pdf_document import PDFDocument
        from datetime import datetime

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
        mock_service = MagicMock()
        mock_service.get_persisted_document.return_value = doc

        use_case = DownloadExtractedText(mock_service)
        result = use_case.execute("507f1f77bcf86cd799439011")

        assert result == "Extracted text content"

    """Descargar texto de PDF inexistente lanza exception."""

    def test_raises_exception(self):
        mock_service = MagicMock()
        mock_service.get_persisted_document.return_value = None

        use_case = DownloadExtractedText(mock_service)
        with pytest.raises(PDFNotFoundException):
            use_case.execute("nonexistent")
