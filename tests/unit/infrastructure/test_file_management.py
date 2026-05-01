"""Tests para operaciones de gestión de archivos."""

import pytest

from app.exceptions import InvalidFileException
from app.infrastructure import pdf_extractor
from app.repositories.file_pdf_repository import FilePDFRepository


class TestFileNotFound:
    @pytest.mark.asyncio
    async def test_returns_none_when_file_not_found(self, temp_file_repository):
        result = await temp_file_repository.get("non-existent-id-12345")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_false_when_deleting_nonexistent_file(self, temp_file_repository):
        result = await temp_file_repository.delete("non-existent-id-12345")
        assert result is False


class TestInvalidFileContent:
    @pytest.mark.asyncio
    async def test_raises_exception_for_zero_byte_file(self, pdf_service):
        with pytest.raises(InvalidFileException) as exc_info:
            await pdf_service.process_pdf(b"", "test.pdf")
        assert "empty" in str(exc_info.value).lower()

    def test_raises_exception_for_corrupt_pdf(self):
        corrupt_content = b"This is not a PDF file\x00\x01\x02\x03"
        with pytest.raises(Exception) as exc_info:
            pdf_extractor.extract_text(corrupt_content)

        error_message = str(exc_info.value).lower()
        assert "pdf" in error_message or "stream" in error_message or "read" in error_message

    @pytest.mark.asyncio
    async def test_raises_exception_for_empty_filename(self, pdf_service):
        valid_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n>>"
        with pytest.raises(InvalidFileException) as exc_info:
            await pdf_service.process_pdf(valid_content, "")
        assert "empty" in str(exc_info.value).lower()


class TestFileSystemEdgeCases:
    @pytest.mark.parametrize(
        "filename",
        [
            "file with spaces.pdf",
            "file-with-dashes.pdf",
            "file_with_underscores.pdf",
            "camelCaseFile.pdf",
            "UPPERCASE.pdf",
        ],
    )
    @pytest.mark.asyncio
    async def test_handles_special_characters_in_filename(self, filename, temp_file_repository):
        content = b"%PDF-1.4 test content"
        saved_path = await temp_file_repository.save(content, filename)

        assert saved_path.exists()
        assert saved_path.name.endswith(f"_{filename}")
        saved_path.unlink()

    @pytest.mark.asyncio
    async def test_creates_unique_paths_for_duplicate_filenames(self, temp_file_repository):
        filename = "duplicate.pdf"
        content = b"%PDF-1.4 test content"

        path1 = await temp_file_repository.save(content, filename)
        path2 = await temp_file_repository.save(content, filename)

        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

        path1.unlink()
        path2.unlink()
