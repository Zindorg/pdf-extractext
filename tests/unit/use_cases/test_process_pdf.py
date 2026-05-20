"""Tests para el caso de uso ProcessPDFFile."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import DuplicateDocumentException, InvalidFileException, PDFExtractionException
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
        mock_svc = MagicMock()
        mock_svc.process_pdf = AsyncMock(return_value=doc)

        use_case = ProcessPDFFile(mock_svc)
        result = await use_case.execute(b"pdf content", "test.pdf")

        assert result == doc
        assert result.filename == "test.pdf"

    """Procesar un PDF vacio lanza exception."""

    async def test_raises_exception(self):
        mock_svc = MagicMock()
        mock_svc.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File is empty")
        )

        use_case = ProcessPDFFile(mock_svc)
        with pytest.raises(InvalidFileException):
            await use_case.execute(b"", "test.pdf")

    """Procesar un PDF ya existente lanza exception."""

    async def test_raises_on_duplicate(self):
        mock_svc = MagicMock()
        mock_svc.process_pdf = AsyncMock(
            side_effect=DuplicateDocumentException("Duplicate")
        )

        use_case = ProcessPDFFile(mock_svc)
        with pytest.raises(DuplicateDocumentException):
            await use_case.execute(b"pdf content", "test.pdf")
