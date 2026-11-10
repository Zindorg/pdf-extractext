"""Invariantes de un archivo subido (app/domain/uploaded_file.py)."""

import hashlib

import pytest

from app.domain.exceptions import InvalidFileException
from app.domain.uploaded_file import UploadedFile


class TestCreation:
    @pytest.mark.parametrize("filename", ["", "   "])
    def test_rejects_empty_or_blank_name(self, filename):
        with pytest.raises(InvalidFileException, match="empty"):
            UploadedFile(filename=filename, content=b"x")

    @pytest.mark.parametrize(
        "filename",
        ["document.txt", "document.doc", "document.docx", "image.png", "image.jpg", "document"],
    )
    def test_rejects_non_pdf_name(self, filename):
        with pytest.raises(InvalidFileException, match="PDF"):
            UploadedFile(filename=filename, content=b"x")

    @pytest.mark.parametrize(
        "filename",
        ["document.pdf", "document.PDF", "document.Pdf", "document.pDf", "path/to/document.pdf"],
    )
    def test_accepts_pdf_name_in_any_case(self, filename):
        assert UploadedFile(filename=filename, content=b"x").filename == filename

    def test_rejects_empty_content(self):
        with pytest.raises(InvalidFileException, match="empty"):
            UploadedFile(filename="a.pdf", content=b"")


class TestSize:
    def test_size_is_content_length(self):
        assert UploadedFile(filename="a.pdf", content=b"12345").size == 5

    def test_accepts_up_to_the_limit(self):
        UploadedFile(filename="a.pdf", content=b"x" * 10).ensure_not_larger_than(10)

    def test_rejects_over_the_limit(self):
        with pytest.raises(InvalidFileException, match="too large"):
            UploadedFile(filename="a.pdf", content=b"x" * 11).ensure_not_larger_than(10)


class TestChecksum:
    def test_is_sha256_of_content(self):
        file = UploadedFile(filename="a.pdf", content=b"abc")
        assert file.checksum == hashlib.sha256(b"abc").hexdigest()

    def test_same_content_same_checksum_regardless_of_name(self):
        assert (
            UploadedFile(filename="a.pdf", content=b"same").checksum
            == UploadedFile(filename="b.pdf", content=b"same").checksum
        )

    def test_different_content_different_checksum(self):
        assert (
            UploadedFile(filename="a.pdf", content=b"one").checksum
            != UploadedFile(filename="a.pdf", content=b"two").checksum
        )
