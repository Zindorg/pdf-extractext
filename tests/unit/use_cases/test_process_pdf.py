"""Tests para el caso de uso ProcessPDFFile."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import DuplicateDocumentException, InvalidFileException
from app.models.pdf_document import PDFDocument
from app.use_cases.process_pdf import ProcessPDFFile


class TestProcessPdfFile:
    """Procesar un PDF valido retorna el documento creado."""

    async def test_returns_document(self):
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
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(return_value=doc)

        mock_queries = MagicMock()

        use_case = ProcessPDFFile(mock_extraction, mock_queries)
        result = await use_case.execute(b"pdf content", "test.pdf")

        assert result["filename"] == "test.pdf"
        assert result["page_count"] == 5
        assert result["file_size"] == 1024
        assert result["text_preview"] == "Extracted text"
        assert result["checksum"] == "abc123"
        assert result["is_duplicate"] is False
        assert result["id"] is not None

    """Procesar un PDF vacio lanza exception."""

    async def test_raises_exception(self):
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File is empty")
        )

        mock_queries = MagicMock()

        use_case = ProcessPDFFile(mock_extraction, mock_queries)
        with pytest.raises(InvalidFileException):
            await use_case.execute(b"", "test.pdf")

    """Procesar un PDF ya existente lanza exception."""

    async def test_raises_on_duplicate(self):
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(
            side_effect=DuplicateDocumentException("Duplicate")
        )

        mock_queries = MagicMock()

        use_case = ProcessPDFFile(mock_extraction, mock_queries)
        with pytest.raises(DuplicateDocumentException):
            await use_case.execute(b"pdf content", "test.pdf")
