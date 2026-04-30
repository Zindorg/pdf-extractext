"""Unit tests for file management operations."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from app.repositories.file_pdf_repository import FilePDFRepository
from app.services.pdf_service import PDFService
from app.infrastructure import pdf_extractor
from app.exceptions import InvalidFileException


class TestFileNotFound:
    """Tests for scenarios where files do not exist."""

    @pytest.fixture
    def temp_upload_dir(self, tmp_path):
        """Create a temporary upload directory."""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        return upload_dir

    @pytest.fixture
    def repository_with_temp_dir(self, temp_upload_dir, monkeypatch):
        """Create FilePDFRepository with temporary upload directory."""
        from app.config import Settings

        mock_settings = Settings(upload_dir=str(temp_upload_dir))
        monkeypatch.setattr("app.repositories.file_pdf_repository.settings", mock_settings)

        return FilePDFRepository()

    @pytest.mark.asyncio
    async def test_returns_none_when_file_not_found(
        self, repository_with_temp_dir
    ):
        """Repository returns None when file ID does not exist."""
        result = await repository_with_temp_dir.get("non-existent-id-12345")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_false_when_deleting_nonexistent_file(
        self, repository_with_temp_dir
    ):
        """Delete returns False when file does not exist."""
        result = await repository_with_temp_dir.delete("non-existent-id-12345")
        assert result is False


class TestInvalidFileContent:
    """Tests for files with invalid or corrupt content."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        mock = MagicMock()
        mock.save = AsyncMock(return_value=Path("/tmp/test.pdf"))
        mock.get = AsyncMock(return_value=None)
        return mock

    @pytest.fixture
    def service_with_mock_repo(self, mock_repository):
        """Create PDFService with mocked repository."""
        return PDFService(mock_repository)

    @pytest.mark.asyncio
    async def test_raises_exception_for_zero_byte_file(
        self, service_with_mock_repo
    ):
        """Service raises InvalidFileException for zero-byte files."""
        with pytest.raises(InvalidFileException) as exc_info:
            await service_with_mock_repo.process_pdf(b"", "test.pdf")

        assert "empty" in str(exc_info.value).lower()

    def test_raises_exception_for_corrupt_pdf(self):
        """Extractor raises exception when PDF format is invalid."""
        corrupt_content = b"This is not a PDF file\x00\x01\x02\x03"

        with pytest.raises(Exception) as exc_info:
            pdf_extractor.extract_text(corrupt_content)

        error_message = str(exc_info.value).lower()
        assert "pdf" in error_message or "stream" in error_message or "read" in error_message

    @pytest.mark.asyncio
    async def test_raises_exception_for_empty_filename(
        self, service_with_mock_repo
    ):
        """Service raises InvalidFileException for empty filename."""
        valid_content = (
            b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n>>"
        )

        with pytest.raises(InvalidFileException) as exc_info:
            await service_with_mock_repo.process_pdf(valid_content, "")

        assert "empty" in str(exc_info.value).lower()


class TestFileSystemEdgeCases:
    """Tests for filesystem-related edge cases."""

    @pytest.mark.asyncio
    async def test_handles_special_characters_in_filename(
        self, tmp_path, monkeypatch
    ):
        """Repository handles filenames with special characters."""
        from app.config import Settings

        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()

        mock_settings = Settings(upload_dir=str(upload_dir))
        monkeypatch.setattr("app.repositories.file_pdf_repository.settings", mock_settings)

        repository = FilePDFRepository()

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
            saved_path.unlink()

    @pytest.mark.asyncio
    async def test_creates_unique_paths_for_duplicate_filenames(
        self, tmp_path, monkeypatch
    ):
        """Repository creates unique paths for files with same name."""
        from app.config import Settings

        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()

        mock_settings = Settings(upload_dir=str(upload_dir))
        monkeypatch.setattr("app.repositories.file_pdf_repository.settings", mock_settings)

        repository = FilePDFRepository()
        filename = "duplicate.pdf"
        content = b"%PDF-1.4 test content"

        path1 = await repository.save(content, filename)
        path2 = await repository.save(content, filename)

        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

        path1.unlink()
        path2.unlink()
