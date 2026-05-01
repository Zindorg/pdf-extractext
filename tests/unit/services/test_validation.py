"""Tests para funciones de validación del servicio PDF."""

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import _validate_content, _validate_filename


class TestFilenameValidation:
    def test_rejects_empty_filename(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("")

    def test_rejects_whitespace_only_filename(self):
        with pytest.raises(InvalidFileException):
            _validate_filename("   ")

    @pytest.mark.parametrize(
        "filename",
        [
            "document.txt",
            "document.doc",
            "document.docx",
            "image.png",
            "image.jpg",
            "document",
        ],
    )
    def test_rejects_non_pdf_extensions(self, filename):
        with pytest.raises(InvalidFileException):
            _validate_filename(filename)

    @pytest.mark.parametrize(
        "filename", ["document.pdf", "document.PDF", "document.Pdf", "document.pDf"]
    )
    def test_accepts_pdf_any_case(self, filename):
        assert _validate_filename(filename) is None  # no raise

    def test_accepts_path_with_pdf_extension(self):
        assert _validate_filename("path/to/document.pdf") is None


class TestContentValidation:
    def test_rejects_empty_content(self):
        with pytest.raises(InvalidFileException):
            _validate_content(b"")

    def test_accepts_valid_content(self):
        assert _validate_content(b"some content") is None


class TestPDFServiceValidation:
    @pytest.mark.asyncio
    async def test_rejects_empty_filename(self, pdf_service, valid_pdf_content):
        with pytest.raises(InvalidFileException):
            await pdf_service.process_pdf(valid_pdf_content, "")

    @pytest.mark.asyncio
    async def test_rejects_empty_content(self, pdf_service):
        with pytest.raises(InvalidFileException):
            await pdf_service.process_pdf(b"", "document.pdf")

    @pytest.mark.asyncio
    async def test_accepts_valid_pdf(self, pdf_service, valid_pdf_content, mock_repository):
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
