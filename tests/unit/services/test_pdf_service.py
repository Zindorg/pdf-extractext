"""Tests para PDFService: sanitización, generación de texto y limpieza."""

import re
import tempfile
from pathlib import Path

import pytest

from app.exceptions import InvalidFileException
from app.services.pdf_service import PDFService, _sanitize_filename


class TestSanitizeFilename:
    def test_removes_pdf_extension(self):
        assert not _sanitize_filename("document.pdf").endswith(".pdf")

    def test_replaces_special_chars_with_underscore(self):
        result = _sanitize_filename("doc & file [2024].pdf")
        assert not any(ch in result for ch in "&[]")

    def test_limits_to_50_chars(self):
        long_name = "a" * 100 + ".pdf"
        assert len(_sanitize_filename(long_name)) <= 50

    def test_sanitizes_all_special_chars(self):
        result = _sanitize_filename("!@#$.pdf")
        assert not any(ch in result for ch in "!@#$")


class TestGenerateTextFile:
    def test_returns_text_and_path(self, pdf_service, valid_pdf_content):
        text, path = pdf_service.generate_text_file(valid_pdf_content, "doc.pdf")
        assert isinstance(text, str)
        assert isinstance(path, Path)
        assert path.suffix == ".txt"

    def test_extracted_text_is_string(self, pdf_service, valid_pdf_content):
        text, _ = pdf_service.generate_text_file(valid_pdf_content, "test.pdf")
        assert isinstance(text, str)

    def test_txt_created_in_temp_directory(self, pdf_service, valid_pdf_content):
        _, path = pdf_service.generate_text_file(valid_pdf_content, "doc.pdf")
        assert path.exists()
        assert path.parent == Path(tempfile.gettempdir())

    def test_filename_is_sanitized(self, pdf_service, valid_pdf_content):
        _, path = pdf_service.generate_text_file(
            valid_pdf_content, "doc with spaces & special.pdf"
        )
        assert " " not in path.name
        assert "&" not in path.name
        assert re.match(r"^[a-zA-Z0-9_]+_.*\.txt$", path.name)

    def test_txt_is_utf8_encoded(self, pdf_service, valid_pdf_content):
        text, path = pdf_service.generate_text_file(valid_pdf_content, "doc.pdf")
        content = path.read_text(encoding="utf-8")
        assert content == text

    def test_rejects_empty_content(self, pdf_service):
        with pytest.raises(InvalidFileException):
            pdf_service.generate_text_file(b"", "doc.pdf")

    def test_rejects_empty_filename(self, pdf_service, valid_pdf_content):
        with pytest.raises(InvalidFileException):
            pdf_service.generate_text_file(valid_pdf_content, "")


class TestCleanupMemory:
    def test_cleanup_method_exists(self, pdf_service):
        assert hasattr(pdf_service, "cleanup_memory")

    def test_cleanup_returns_none(self, pdf_service):
        assert pdf_service.cleanup_memory() is None
