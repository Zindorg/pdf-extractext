"""Reglas puras sobre archivos subidos (app/domain/pdf_rules.py)."""

import hashlib

import pytest

from app.domain.pdf_rules import (
    generate_checksum,
    validate_content,
    validate_filename,
    validate_size,
)
from app.exceptions import InvalidFileException


class TestValidateFilename:
    @pytest.mark.parametrize("filename", ["", "   "])
    def test_rejects_empty_or_blank(self, filename):
        with pytest.raises(InvalidFileException):
            validate_filename(filename)

    @pytest.mark.parametrize(
        "filename",
        ["document.txt", "document.doc", "document.docx", "image.png", "image.jpg", "document"],
    )
    def test_rejects_non_pdf(self, filename):
        with pytest.raises(InvalidFileException, match="PDF"):
            validate_filename(filename)

    @pytest.mark.parametrize(
        "filename",
        ["document.pdf", "document.PDF", "document.Pdf", "document.pDf", "path/to/document.pdf"],
    )
    def test_accepts_pdf_in_any_case(self, filename):
        validate_filename(filename)


class TestValidateContent:
    def test_rejects_empty(self):
        with pytest.raises(InvalidFileException, match="empty"):
            validate_content(b"")

    def test_accepts_non_empty(self):
        validate_content(b"some content")


class TestValidateSize:
    def test_accepts_up_to_the_limit(self):
        validate_size(b"x" * 10, max_size=10)

    def test_rejects_over_the_limit(self):
        with pytest.raises(InvalidFileException, match="too large"):
            validate_size(b"x" * 11, max_size=10)


class TestGenerateChecksum:
    def test_is_sha256_hex_digest(self):
        assert generate_checksum(b"abc") == hashlib.sha256(b"abc").hexdigest()

    def test_is_deterministic(self):
        assert generate_checksum(b"same") == generate_checksum(b"same")

    def test_differs_for_different_content(self):
        assert generate_checksum(b"one") != generate_checksum(b"two")
