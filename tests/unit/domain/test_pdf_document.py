"""Construcción de PDFDocument a partir de una subida."""

from datetime import datetime

import pytest

from app.domain.exceptions import PDFExtractionException
from app.domain.pdf_document import PDFDocument
from app.domain.uploaded_file import UploadedFile

FILE = UploadedFile(filename="informe.pdf", content=b"%PDF bytes")


def test_from_upload_takes_identity_and_size_from_the_file():
    doc = PDFDocument.from_upload(FILE, text="Hola", page_count=3)

    assert doc.id is None
    assert doc.checksum == FILE.checksum
    assert doc.filename == "informe.pdf"
    assert doc.file_size == FILE.size
    assert doc.text_content == "Hola"
    assert doc.page_count == 3


def test_new_documents_get_creation_timestamps():
    doc = PDFDocument.from_upload(FILE, text="Hola", page_count=1)

    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)


@pytest.mark.parametrize("text", ["", "   ", "\n\n"])
def test_pdf_without_text_is_rejected(text):
    with pytest.raises(PDFExtractionException, match="No text"):
        PDFDocument.from_upload(FILE, text=text, page_count=1)
