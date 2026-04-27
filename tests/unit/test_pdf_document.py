"""Tests for PDFDocument domain model."""

from datetime import datetime

import pytest

from models.pdf_document import PDFDocument


class TestPDFDocumentCreation:
    """Tests for PDF document creation."""

    def test_pdf_document_has_checksum_field(self):
        """Should have checksum field."""
        doc = PDFDocument(
            filename="test.pdf",
            checksum="aabbccdd...",
            text_content="sample content",
            page_count=1,
            file_size=100
        )
        assert hasattr(doc, 'checksum')
        assert doc.checksum == "aabbccdd..."

    def test_pdf_document_requires_checksum(self):
        """Should require checksum on creation."""
        with pytest.raises(TypeError):
            PDFDocument(filename="test.pdf")

    def test_pdf_document_timestamps_auto_set(self):
        """Should auto-set timestamps if not provided."""
        doc = PDFDocument(
            filename="test.pdf",
            checksum="abc123",
            text_content=""
        )
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)


class TestPDFDocumentUpdate:
    """Tests for updating PDF document."""

    def test_update_text_updates_timestamp(self):
        """Should update timestamp when text is updated."""
        import time

        doc = PDFDocument(
            filename="test.pdf",
            checksum="abc123",
            text_content="initial"
        )
        original_updated = doc.updated_at

        time.sleep(0.01)  # Small delay to ensure different timestamp
        doc.update_text("updated content")

        assert doc.text_content == "updated content"
        assert doc.updated_at >= original_updated
