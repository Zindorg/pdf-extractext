"""Tests para creacion de PDFDocument."""

from datetime import datetime

import pytest

from app.models.pdf_document import PDFDocument


class TestPdfDocumentCreationHasChecksum:
    """PDFDocument tiene campo checksum."""

    def test_has_checksum_field(self):
        doc = PDFDocument(
            filename="test.pdf",
            checksum="aabbccdd...",
            text_content="sample content",
            page_count=1,
            file_size=100,
        )
        assert hasattr(doc, "checksum")
        assert doc.checksum == "aabbccdd..."

    """PDFDocument requiere checksum."""

    def test_requires_checksum(self):
        with pytest.raises(TypeError):
            PDFDocument(filename="test.pdf")
    
    """PDFDocument establece timestamps automaticamente."""

    def test_timestamps_auto_set(self):
        doc = PDFDocument(
            filename="test.pdf",
            checksum="abc123",
            text_content="",
        )
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)
