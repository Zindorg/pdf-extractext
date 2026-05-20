"""Tests para validacion a nivel de servicio PDF."""

import pytest

from app.exceptions import InvalidFileException

class TestPdfService:
    """Servicio rechaza filename vacio."""

    @pytest.mark.asyncio
    async def test_raises_exception(self, pdf_service, valid_pdf_content):
        with pytest.raises(InvalidFileException):
            await pdf_service.process_pdf(valid_pdf_content, "")
    
    """Servicio rechaza contenido vacio."""

    @pytest.mark.asyncio
    async def test_raises_exception(self, pdf_service):
        with pytest.raises(InvalidFileException):
            await pdf_service.process_pdf(b"", "document.pdf")

    """Servicio acepta PDF valido."""

    @pytest.mark.asyncio
    async def test_accepts_valid(self, pdf_service, valid_pdf_content, mock_repository):
        from app.models.pdf_document import PDFDocument

        def mock_create(document):
            document.id = "abc123"
            return document

        mock_repository.find_by_checksum.return_value = None
        mock_repository.create.side_effect = mock_create

        result = await pdf_service.process_pdf(valid_pdf_content, "document.pdf")

        assert result.filename == "document.pdf"
        assert result.file_size == len(valid_pdf_content)
        assert result.checksum is not None
