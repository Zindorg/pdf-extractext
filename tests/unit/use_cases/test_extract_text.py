"""Tests para el caso de uso ExtractText."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.pdf_document import PDFDocument
from datetime import datetime
from app.exceptions import PDFNotFoundException
from app.use_cases.extract_text import ExtractText


class TestExtractText:
    """Extraer texto de PDF existente."""

    @pytest.mark.asyncio
    async def test_returns_text(self):

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
        mock_service = MagicMock()
        mock_service.get_persisted_document = AsyncMock(return_value=doc)

        use_case = ExtractText(mock_service)
        result = await use_case.execute("507f1f77bcf86cd799439011")

        assert result.text == "Extracted text"
        assert result.pages_extracted == 5
    
    """Extraer texto de PDF inexistente lanza exception."""

    @pytest.mark.asyncio
    async def test_raises_exception(self):
        mock_service = MagicMock()
        mock_service.get_persisted_document = AsyncMock(
            side_effect=PDFNotFoundException("Not found")
        )

        use_case = ExtractText(mock_service)
        with pytest.raises(PDFNotFoundException):
            await use_case.execute("nonexistent")