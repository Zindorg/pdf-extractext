"""Unit tests for PDFService input validation."""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from core.exceptions import InvalidFileException
from services.pdf_service import _validate_filename, _validate_content


class TestFilenameValidation:
    """Tests for filename validation function."""

    def test_rejects_empty_filename(self):
        """Should reject empty filename."""
        with pytest.raises(InvalidFileException):
            _validate_filename("")

    def test_rejects_whitespace_only_filename(self):
        """Should reject whitespace-only filename."""
        with pytest.raises(InvalidFileException):
            _validate_filename("   ")

    def test_rejects_non_pdf_extensions(self):
        """Should reject non-PDF extensions."""
        non_pdf_files = [
            "document.txt",
            "document.doc",
            "document.docx",
            "image.png",
            "image.jpg",
            "document",
        ]

        for filename in non_pdf_files:
            with pytest.raises(InvalidFileException):
                _validate_filename(filename)

    def test_accepts_pdf_any_case(self):
        """Should accept .pdf extension in any case."""
        # Any case should be accepted
        _validate_filename("document.pdf")
        _validate_filename("document.PDF")
        _validate_filename("document.Pdf")
        _validate_filename("document.pDf")

    def test_accepts_lowercase_pdf_extension(self):
        """Should accept lowercase .pdf extension."""
        # Should not raise
        _validate_filename("document.pdf")
        _validate_filename("path/to/document.pdf")


class TestContentValidation:
    """Tests for content validation function."""

    def test_rejects_empty_content(self):
        """Should reject empty file content."""
        with pytest.raises(InvalidFileException):
            _validate_content(b"")

    def test_accepts_valid_content(self):
        """Should accept non-empty content."""
        # Should not raise
        _validate_content(b"some content")


class TestPDFServiceValidation:
    """Tests for PDFService validation integration."""

    @pytest.mark.asyncio
    async def test_rejects_empty_filename(self, pdf_service, valid_pdf_content):
        """Should reject empty filename at service level."""
        with pytest.raises(InvalidFileException):
            await pdf_service.process_pdf(valid_pdf_content, "")

    @pytest.mark.asyncio
    async def test_rejects_empty_content(self, pdf_service):
        """Should reject empty file content at service level."""
        with pytest.raises(InvalidFileException):
            await pdf_service.process_pdf(b"", "document.pdf")

    @pytest.mark.asyncio
    async def test_accepts_valid_pdf(
        self, pdf_service, valid_pdf_content, mock_repository
    ):
        """Should accept valid PDF file."""
        mock_repository.save = AsyncMock(
            return_value=Path("/fake/path/abc123_document.pdf")
        )

        result = await pdf_service.process_pdf(valid_pdf_content, "document.pdf")

        assert result.filename == "document.pdf"
        assert result.file_size == len(valid_pdf_content)
