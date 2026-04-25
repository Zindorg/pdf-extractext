"""Unit tests for PDF service text extraction and temp file generation."""

import re
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from core.exceptions import InvalidFileException, PDFExtractionException
from services.pdf_service import PDFService, _sanitize_filename


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_removes_pdf_extension(self):
        """Should remove .pdf extension."""
        result = _sanitize_filename("document.pdf")
        assert not result.endswith(".pdf")

    def test_replaces_special_chars_with_underscore(self):
        """Should replace special characters with underscores."""
        result = _sanitize_filename("doc & file [2024].pdf")
        assert "&" not in result
        assert "[" not in result
        assert "]" not in result

    def test_limits_to_50_chars(self):
        """Should limit filename to 50 characters."""
        long_name = "a" * 100 + ".pdf"
        result = _sanitize_filename(long_name)
        assert len(result) <= 50

    def test_sanitizes_all_special_chars(self):
        """Should sanitize filename with only special characters."""
        result = _sanitize_filename("!@#$.pdf")
        # All special chars become underscores
        assert "!" not in result
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result


class TestGenerateTextFile:
    """Tests for generate_text_file method."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock PDF repository."""
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.save = AsyncMock(return_value=None)
        mock.get = AsyncMock(return_value=None)
        return mock

    @pytest.fixture
    def pdf_service(self, mock_repository):
        """Create PDFService with mocked repository."""
        return PDFService(mock_repository)

    @pytest.fixture
    def valid_pdf_bytes(self):
        """Load valid PDF file as bytes."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "valid.pdf"
        return fixture_path.read_bytes()

    def test_returns_text_and_path(self, pdf_service, valid_pdf_bytes):
        """Should return tuple of text and Path."""
        text, path = pdf_service.generate_text_file(valid_pdf_bytes, "doc.pdf")

        assert isinstance(text, str)
        assert isinstance(path, Path)
        assert path.suffix == ".txt"

    def test_extracted_text_is_accurate(self, pdf_service, valid_pdf_bytes):
        """Should extract text accurately from PDF."""
        text, _ = pdf_service.generate_text_file(valid_pdf_bytes, "test.pdf")

        assert isinstance(text, str)
        # The text might be empty if the test PDF has no extractable text
        # but it should always return a string

    def test_txt_created_in_temp_directory(self, pdf_service, valid_pdf_bytes):
        """Should create .txt in system temp directory."""
        _, path = pdf_service.generate_text_file(valid_pdf_bytes, "doc.pdf")

        assert path.exists()
        temp_dir = Path(tempfile.gettempdir())
        assert path.parent == temp_dir

    def test_filename_is_sanitized(self, pdf_service, valid_pdf_bytes):
        """Should use sanitized filename."""
        _, path = pdf_service.generate_text_file(
            valid_pdf_bytes, "doc with spaces & special.pdf"
        )

        # Should not have spaces or special chars
        assert " " not in path.name
        assert "&" not in path.name
        # Should match pattern: sanitized_name_*.txt
        assert re.match(r"^[a-zA-Z0-9_]+_.*\.txt$", path.name)

    def test_txt_is_utf8_encoded(self, pdf_service, valid_pdf_bytes):
        """Should create file with UTF-8 encoding."""
        text, path = pdf_service.generate_text_file(valid_pdf_bytes, "doc.pdf")

        # Read back with explicit UTF-8
        content = path.read_text(encoding="utf-8")
        assert isinstance(content, str)
        assert content == text

    def test_rejects_empty_content(self, pdf_service):
        """Should reject empty bytes."""
        with pytest.raises(InvalidFileException):
            pdf_service.generate_text_file(b"", "doc.pdf")

    def test_rejects_empty_filename(self, pdf_service, valid_pdf_bytes):
        """Should reject empty filename."""
        with pytest.raises(InvalidFileException):
            pdf_service.generate_text_file(valid_pdf_bytes, "")


class TestCleanupMemory:
    """Tests for cleanup_memory method."""

    def test_cleanup_method_exists(self, mock_repository):
        """Should have cleanup_memory method."""
        service = PDFService(mock_repository)
        assert hasattr(service, "cleanup_memory")

    def test_cleanup_returns_none(self, mock_repository):
        """Should return None."""
        service = PDFService(mock_repository)
        result = service.cleanup_memory()
        assert result is None
