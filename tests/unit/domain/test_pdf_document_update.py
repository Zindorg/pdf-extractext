"""Tests para actualizacion de PDFDocument."""

from time import sleep

from app.models.pdf_document import PDFDocument


class TestPdfDocumentUpdateTextUpdatesTimestamp:
    """Actualizar texto actualiza timestamp."""

    def test_updates_timestamp(self):
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
