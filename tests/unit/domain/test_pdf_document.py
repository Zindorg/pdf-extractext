"""Tests para PDFDocument (modelo de dominio)."""

from datetime import datetime
from time import sleep

import pytest

from app.models.pdf_document import PDFDocument


class TestPDFDocumentCreation:
    """Tests para la creación de documentos PDF."""

    def test_pdf_document_has_checksum_field(self):
        doc = PDFDocument(
            filename="test.pdf",
            checksum="aabbccdd...",
            text_content="sample content",
            page_count=1,
            file_size=100,
        )
        assert hasattr(doc, "checksum")
        assert doc.checksum == "aabbccdd..."

    def test_pdf_document_requires_checksum(self):
        with pytest.raises(TypeError):
            PDFDocument(filename="test.pdf")

    def test_pdf_document_timestamps_auto_set(self):
        doc = PDFDocument(
            filename="test.pdf",
            checksum="abc123",
            text_content="",
        )
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)


class TestPDFDocumentUpdate:
    """Tests para la actualización de documentos PDF."""

    def test_update_text_updates_timestamp(self):
        doc = PDFDocument(
            filename="test.pdf",
            checksum="abc123",
            text_content="initial",
        )
        original_updated = doc.updated_at

        sleep(0.01)
        doc.update_text("updated content")

        assert doc.text_content == "updated content"
        assert doc.updated_at >= original_updated
