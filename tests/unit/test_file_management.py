"""Unit tests for file management operations.

Tests cover file handling edge cases including missing files,
corrupt files, and zero-byte files.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from repositories.pdf_repository import PDFRepository
from services.pdf_service import PDFService
from infrastructure.pdf_extractor_adapter import PDFExtractorAdapter
from core.exceptions import PDFExtractionException, InvalidFileException


class TestFileNotFound:
    """Tests for scenarios where files do not exist."""

    @pytest.fixture
    def temp_upload_dir(self, tmp_path):
        """Create a temporary upload directory.

        Returns:
            Path: Temporary directory path.
        """
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        return upload_dir

    @pytest.fixture
    def repository_with_temp_dir(self, temp_upload_dir, monkeypatch):
        """Create PDFRepository with temporary upload directory.

        Args:
            temp_upload_dir: Temporary directory fixture.
            monkeypatch: Pytest monkeypatch fixture.

        Returns:
            PDFRepository: Repository configured with temp directory.
        """
        from core.config import Settings

        mock_settings = Settings(upload_dir=str(temp_upload_dir))
        monkeypatch.setattr("repositories.pdf_repository.settings", mock_settings)

        return PDFRepository()

    @pytest.mark.asyncio
    async def test_should_return_none_when_file_not_found_in_repository(
        self, repository_with_temp_dir
    ):
        """Repository returns None when file ID does not exist.

        Scenario: Querying for a non-existent file ID should return None
        rather than raising an exception.
        """
        result = await repository_with_temp_dir.get("non-existent-id-12345")

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_extracting_from_nonexistent_file(
        self, temp_upload_dir, monkeypatch
    ):
        """Service raises PDFExtractionException when file not found.

        Scenario: Attempting to extract text from a file ID that does not
        exist should raise PDFExtractionException with appropriate message.
        """
        from core.config import Settings

        mock_settings = Settings(upload_dir=str(temp_upload_dir))
        monkeypatch.setattr("repositories.pdf_repository.settings", mock_settings)

        repository = PDFRepository()
        mock_extractor = MagicMock(spec=PDFExtractorAdapter)
        service = PDFService(repository, mock_extractor)

        with pytest.raises(PDFExtractionException) as exc_info:
            await service.extract_text_from_pdf("non-existent-file-id")

        assert "PDF not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_should_return_false_when_deleting_nonexistent_file(
        self, repository_with_temp_dir
    ):
        """Delete returns False when file does not exist.

        Scenario: Attempting to delete a file ID that does not exist
        should return False without raising an exception.
        """
        result = await repository_with_temp_dir.delete("non-existent-id-12345")

        assert result is False


class TestInvalidFileContent:
    """Tests for files with invalid or corrupt content."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository that simulates successful save.

        Returns:
            MagicMock: Mocked repository interface.
        """
        mock = MagicMock()
        mock.save = AsyncMock(return_value=Path("/tmp/test.pdf"))
        mock.get = AsyncMock(return_value=None)
        return mock

    @pytest.fixture
    def service_with_mock_repo(self, mock_repository):
        """Create PDFService with mocked repository and real extractor.

        Args:
            mock_repository: Mocked repository fixture.

        Returns:
            PDFService: Service with mocked repository.
        """
        extractor = PDFExtractorAdapter()
        return PDFService(mock_repository, extractor)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_file_is_zero_bytes(
        self, service_with_mock_repo
    ):
        """Service raises InvalidFileException for zero-byte files.

        Scenario: Uploading a file with no content (0 bytes) should
        raise InvalidFileException indicating the file is empty.
        """
        empty_content = b""

        with pytest.raises(InvalidFileException) as exc_info:
            await service_with_mock_repo.process_pdf(empty_content, "test.pdf")

        assert "File is empty" in str(exc_info.value)

    def test_should_raise_exception_when_pdf_is_corrupt(self):
        """Extractor raises exception when PDF format is invalid.

        Scenario: Attempting to extract text from content that is not
        a valid PDF (random bytes or broken format) should raise an error.
        """
        extractor = PDFExtractorAdapter()
        corrupt_content = b"This is not a PDF file\x00\x01\x02\x03"

        with pytest.raises(Exception) as exc_info:
            extractor.extract_text(corrupt_content)

        error_message = str(exc_info.value).lower()
        assert (
            "pdf" in error_message
            or "stream" in error_message
            or "read" in error_message
        )

    def test_should_raise_exception_when_pdf_header_is_broken(self):
        """Extractor raises exception when PDF header is malformed.

        Scenario: Content that starts with invalid PDF header
        should be rejected during extraction.
        """
        extractor = PDFExtractorAdapter()
        broken_header_content = b"%PDF-0.0\ninvalid data here"

        with pytest.raises(Exception) as exc_info:
            extractor.extract_text(broken_header_content)

        assert exc_info.value is not None

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_filename_is_empty(
        self, service_with_mock_repo
    ):
        """Service raises InvalidFileException for empty filename.

        Scenario: Uploading a file with empty filename should
        raise InvalidFileException.
        """
        valid_content = (
            b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n>>"
        )

        with pytest.raises(InvalidFileException) as exc_info:
            await service_with_mock_repo.process_pdf(valid_content, "")

        assert "Filename cannot be empty" in str(exc_info.value)


class TestFileSystemEdgeCases:
    """Tests for filesystem-related edge cases."""

    @pytest.mark.asyncio
    async def test_should_handle_special_characters_in_filename(
        self, tmp_path, monkeypatch
    ):
        """Repository handles filenames with special characters.

        Scenario: Files with spaces, unicode, or special characters
        in the name should be saved correctly.
        """
        from core.config import Settings

        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()

        mock_settings = Settings(upload_dir=str(upload_dir))
        monkeypatch.setattr("repositories.pdf_repository.settings", mock_settings)

        repository = PDFRepository()

        special_filenames = [
            "file with spaces.pdf",
            "file-with-dashes.pdf",
            "file_with_underscores.pdf",
            "camelCaseFile.pdf",
            "UPPERCASE.pdf",
        ]

        for filename in special_filenames:
            content = b"%PDF-1.4 test content"
            saved_path = await repository.save(content, filename)

            assert saved_path.exists()
            assert saved_path.name.endswith(f"_{filename}")

            # Cleanup
            saved_path.unlink()

    @pytest.mark.asyncio
    async def test_should_overwrite_when_saving_same_filename_twice(
        self, tmp_path, monkeypatch
    ):
        """Repository creates unique paths for files with same name.

        Scenario: Saving two files with identical names should create
        two distinct files with different UUID prefixes.
        """
        from core.config import Settings

        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()

        mock_settings = Settings(upload_dir=str(upload_dir))
        monkeypatch.setattr("repositories.pdf_repository.settings", mock_settings)

        repository = PDFRepository()
        filename = "duplicate.pdf"
        content = b"%PDF-1.4 test content"

        path1 = await repository.save(content, filename)
        path2 = await repository.save(content, filename)

        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

        # Cleanup
        path1.unlink()
        path2.unlink()
