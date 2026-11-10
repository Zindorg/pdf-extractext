"""Reglas de negocio de la subida, contra fakes (sin pypdf ni MongoDB)."""

import hashlib

import pytest

from app.domain.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractionException,
)
from app.use_cases.upload_pdf import UploadPDF

MAX_SIZE = 100


@pytest.fixture
def upload(repository, extractor):
    return UploadPDF(repository, extractor, max_file_size=MAX_SIZE).execute


class TestSuccessfulUpload:
    def test_persists_document_with_extracted_data(self, upload, repository):
        doc = upload(b"Hola mundo", "informe.pdf")

        stored = repository.find_by_id(doc.id)
        assert stored.filename == "informe.pdf"
        assert stored.text_content == "Hola mundo"
        assert stored.page_count == 1
        assert stored.file_size == len(b"Hola mundo")
        assert stored.checksum == hashlib.sha256(b"Hola mundo").hexdigest()

    def test_accepts_file_of_exactly_max_size(self, upload):
        assert upload(b"x" * MAX_SIZE, "limite.pdf").id is not None


class TestRejectedUpload:
    def test_duplicate_content_is_rejected(self, upload, repository):
        upload(b"mismo contenido", "a.pdf")

        with pytest.raises(DuplicateDocumentException):
            upload(b"mismo contenido", "b.pdf")

        assert len(repository.find_all()) == 1

    def test_file_over_max_size_is_rejected(self, upload, repository):
        with pytest.raises(InvalidFileException, match="too large"):
            upload(b"x" * (MAX_SIZE + 1), "grande.pdf")
        assert repository.find_all() == []

    @pytest.mark.parametrize("content", [b"   ", b"\n\n"])
    def test_pdf_without_text_is_rejected(self, upload, repository, content):
        with pytest.raises(PDFExtractionException, match="No text"):
            upload(content, "vacio.pdf")
        assert repository.find_all() == []

    def test_unreadable_pdf_is_rejected(self, upload):
        with pytest.raises(PDFExtractionException):
            upload(b"CORRUPT", "roto.pdf")

    @pytest.mark.parametrize("filename", ["", "   ", "notas.txt"])
    def test_invalid_filename_is_rejected(self, upload, filename):
        with pytest.raises(InvalidFileException):
            upload(b"texto", filename)

    def test_empty_content_is_rejected(self, upload):
        with pytest.raises(InvalidFileException):
            upload(b"", "vacio.pdf")
