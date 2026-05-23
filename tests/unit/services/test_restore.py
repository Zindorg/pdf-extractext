"""Tests para PDFCommands.restore."""

from datetime import datetime
from unittest.mock import MagicMock

from app.models.pdf_document import PDFDocument
from app.services.pdf_commands import PDFCommands


class TestRestore:
    """Restaurar documento borrado retorna True."""

    def test_returns_true(self):
        doc = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="content",
            page_count=5,
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=datetime.now(),
        )
        mock_repo = MagicMock()
        mock_repo.find_by_id.return_value = doc
        mock_repo.restore.return_value = True

        commands = PDFCommands(repository=mock_repo)
        result = commands.restore("507f1f77bcf86cd799439011")

        assert result is True

    """Restaurar documento no borrado retorna False."""

    def test_returns_false_undeleted(self):
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
        mock_repo = MagicMock()
        mock_repo.find_by_id.return_value = doc

        commands = PDFCommands(repository=mock_repo)
        result = commands.restore("507f1f77bcf86cd799439011")

        assert result is False

    """Restaurar documento inexistente retorna False."""

    def test_returns_false_nonexistent(self):
        mock_repo = MagicMock()
        mock_repo.find_by_id.return_value = None

        commands = PDFCommands(repository=mock_repo)
        result = commands.restore("507f1f77bcf86cd799439011")

        assert result is False
