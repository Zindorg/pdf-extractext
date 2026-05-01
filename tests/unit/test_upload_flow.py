"""Unit tests for the complete process_pdf flow (TDD integration)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractionException,
)
from app.models.pdf_document import PDFDocument
from app.services.pdf_service import PDFService


@pytest.fixture
def mock_repository():
    """Create a mock PDF repository with CRUD methods."""
    mock = MagicMock()
    mock.create = MagicMock(return_value=None)
    mock.find_by_id = MagicMock(return_value=None)
    mock.find_by_checksum = MagicMock(return_value=None)
    mock.find_all = MagicMock(return_value=[])
    mock.update = MagicMock(return_value=None)
    mock.soft_delete = MagicMock(return_value=False)
    mock.delete_by_id = MagicMock(return_value=False)
    mock.restore = MagicMock(return_value=False)
    return mock


@pytest.fixture
def pdf_service(mock_repository):
    """Create PDFService with mocked repository."""
    return PDFService(repository=mock_repository)


class TestProcessPdfHappyPath:
    """Happy path: valid PDF flows through entire pipeline."""

    @patch("app.services.pdf_service.pdf_extractor")
    async def test_process_pdf_valid_input_returns_document(self, mock_extractor, pdf_service, mock_repository):
        """Valid PDF content creates and returns persisted document."""
        mock_extractor.extract_text.return_value = ("Extracted text", 3)

        saved_doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123checksum",
            filename="test.pdf",
            text_content="Extracted text",
            page_count=3,
            file_size=100,
        )
        mock_repository.create.return_value = saved_doc

        result = await pdf_service.process_pdf(b"pdf_content", "test.pdf")

        assert result is not None
        assert result.filename == "test.pdf"
        assert result.text_content == "Extracted text"
        assert result.page_count == 3
        mock_repository.create.assert_called_once()

    @patch("app.services.pdf_service.pdf_extractor")
    async def test_process_pdf_generates_checksum(self, mock_extractor, pdf_service, mock_repository):
        """SHA-256 checksum is generated from file content."""
        mock_extractor.extract_text.return_value = ("text", 1)
        mock_repository.create.return_value = PDFDocument(
            id="123", checksum="", filename="f.pdf", text_content="t"
        )

        content = b"same_content_twice"
        await pdf_service.process_pdf(content, "file.pdf")

        call_args = mock_repository.create.call_args[0][0]
        expected_checksum = pdf_service.generate_checksum(content)
        assert call_args.checksum == expected_checksum

    @patch("app.services.pdf_service.pdf_extractor")
    async def test_process_pdf_stores_file_size(self, mock_extractor, pdf_service, mock_repository):
        """File size is stored from original content length."""
        mock_extractor.extract_text.return_value = ("text", 1)
        mock_repository.create.return_value = PDFDocument(
            id="123", checksum="c", filename="f.pdf", text_content="t"
        )

        content = b"x" * 2048
        await pdf_service.process_pdf(content, "large.pdf")

        call_args = mock_repository.create.call_args[0][0]
        assert call_args.file_size == 2048


class TestProcessPdfDuplicateDetection:
    """Duplicate detection via checksum."""

    @patch("app.services.pdf_service.pdf_extractor")
    async def test_process_pdf_duplicate_raises_exception(self, mock_extractor, pdf_service, mock_repository):
        """Existing checksum raises DuplicateDocumentException."""
        existing = PDFDocument(
            id="existing_id",
            checksum="dup_checksum",
            filename="existing.pdf",
            text_content="old content",
        )
        mock_repository.find_by_checksum.return_value = existing

        with pytest.raises(DuplicateDocumentException) as exc_info:
            await pdf_service.process_pdf(b"content", "new.pdf")

        assert exc_info.value.existing_id == "existing_id"
        mock_extractor.extract_text.assert_not_called()
        mock_repository.create.assert_not_called()

    @patch("app.services.pdf_service.pdf_extractor")
    async def test_process_pdf_non_duplicate_proceeds(self, mock_extractor, pdf_service, mock_repository):
        """No duplicate found allows extraction to proceed."""
        mock_repository.find_by_checksum.return_value = None
        mock_extractor.extract_text.return_value = ("new text", 2)
        mock_repository.create.return_value = PDFDocument(
            id="new_id", checksum="c", filename="n.pdf", text_content="nt"
        )

        result = await pdf_service.process_pdf(b"content", "new.pdf")
        assert result is not None
        mock_extractor.extract_text.assert_called_once()


class TestProcessPdfValidation:
    """Input validation before processing."""

    async def test_process_pdf_empty_filename_raises(self, pdf_service):
        """Empty filename raises InvalidFileException."""
        with pytest.raises(InvalidFileException, match="Filename"):
            await pdf_service.process_pdf(b"content", "")

    async def test_process_pdf_whitespace_filename_raises(self, pdf_service):
        """Whitespace-only filename raises InvalidFileException."""
        with pytest.raises(InvalidFileException, match="whitespace"):
            await pdf_service.process_pdf(b"content", "   ")

    async def test_process_pdf_non_pdf_extension_raises(self, pdf_service):
        """Non-.pdf extension raises InvalidFileException."""
        with pytest.raises(InvalidFileException, match="PDF"):
            await pdf_service.process_pdf(b"content", "file.txt")

    async def test_process_pdf_empty_content_raises(self, pdf_service):
        """Empty bytes content raises InvalidFileException."""
        with pytest.raises(InvalidFileException, match="empty"):
            await pdf_service.process_pdf(b"", "file.pdf")


class TestProcessPdfExtractionFailure:
    """Handling of extraction errors."""

    async def test_process_pdf_extraction_failure_raises(self, pdf_service):
        """pypdf extraction failure raises PDFExtractionException."""
        with patch("app.services.pdf_service.pdf_extractor") as mock_extractor:
            mock_extractor.extract_text.side_effect = Exception("pypdf crashed")
            with pytest.raises(PDFExtractionException, match="Error processing PDF"):
                await pdf_service.process_pdf(b"bad_pdf", "broken.pdf")


class TestChecksumGeneration:
    """Checksum utility method."""

    def test_generate_checksum_deterministic(self, pdf_service):
        """Same content always produces same checksum."""
        content = b"deterministic content"
        c1 = pdf_service.generate_checksum(content)
        c2 = pdf_service.generate_checksum(content)
        assert c1 == c2

    def test_generate_checksum_different_for_different_content(self, pdf_service):
        """Different content produces different checksums."""
        c1 = pdf_service.generate_checksum(b"content_a")
        c2 = pdf_service.generate_checksum(b"content_b")
        assert c1 != c2

    def test_generate_checksum_is_sha256_hex(self, pdf_service):
        """Checksum is a 64-character hex string (SHA-256)."""
        checksum = pdf_service.generate_checksum(b"test")
        assert len(checksum) == 64
        int(checksum, 16)


class TestFindByChecksum:
    """find_by_checksum delegation to repository."""

    def test_find_by_checksum_delegates_to_repository(self, pdf_service, mock_repository):
        """Service delegates find_by_checksum to repository."""
        mock_repository.find_by_checksum.return_value = None
        result = pdf_service.find_by_checksum("abc123")
        mock_repository.find_by_checksum.assert_called_once_with("abc123")
        assert result is None

    def test_find_by_checksum_returns_document(self, pdf_service, mock_repository):
        """Returns document when found by checksum."""
        doc = PDFDocument(
            id="123", checksum="abc", filename="f.pdf", text_content="t"
        )
        mock_repository.find_by_checksum.return_value = doc
        result = pdf_service.find_by_checksum("abc")
        assert result is doc


class TestExtractTextFromPdf:
    """extract_text_from_pdf retrieves stored document."""

    def test_extract_text_returns_existing_document(self, pdf_service, mock_repository):
        """Returns document with already-extracted text from DB."""
        doc = PDFDocument(
            id="123", checksum="c", filename="f.pdf",
            text_content="stored text", page_count=5,
        )
        mock_repository.find_by_id.return_value = doc

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            pdf_service.extract_text_from_pdf("123")
        )
        assert result.text_content == "stored text"

    def test_extract_text_not_found_raises(self, pdf_service, mock_repository):
        """Raises PDFNotFoundException when document missing."""
        from app.exceptions import PDFNotFoundException
        mock_repository.find_by_id.return_value = None

        import asyncio
        with pytest.raises(PDFNotFoundException):
            asyncio.get_event_loop().run_until_complete(
                pdf_service.extract_text_from_pdf("nonexistent")
            )
