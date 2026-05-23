"""Tests para PDFCommands.update_document."""

from datetime import datetime
from unittest.mock import MagicMock

from app.models.pdf_document import PDFDocument
from app.services.pdf_commands import PDFCommands


class TestUpdateDocument:
    """Actualizar documento existente retorna documento actualizado."""

    def test_returns_updated_document(self):
        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="updated.pdf",
            text_content="Updated text",
            page_count=5,
            file_size=2048,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_repo = MagicMock()
        mock_repo.update.return_value = doc

        commands = PDFCommands(repository=mock_repo)
        result = commands.update_document(doc)

        assert result == doc
        assert result.filename == "updated.pdf"

    """Actualizar documento inexistente retorna None."""

    def test_returns_none(self):
        mock_repo = MagicMock()
        mock_repo.update.return_value = None

        commands = PDFCommands(repository=mock_repo)
        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="content",
            page_count=5,
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        result = commands.update_document(doc)

        assert result is None
