"""Tests para PDFService.soft_delete."""

from datetime import datetime
from unittest.mock import MagicMock

from app.models.pdf_document import PDFDocument
from app.services.pdf_service import PDFService


class TestSoftDelete:
    """Soft delete de documento existente retorna True."""

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
        )
        mock_repo = MagicMock()
        mock_repo.find_by_id.return_value = doc
        mock_repo.soft_delete.return_value = True

        service = PDFService(repository=mock_repo)
        result = service.soft_delete("507f1f77bcf86cd799439011")

        assert result is True

    """Soft delete de documento inexistente retorna False."""

    def test_returns_false(self):
        mock_repo = MagicMock()
        mock_repo.find_by_id.return_value = None

        service = PDFService(repository=mock_repo)
        result = service.soft_delete("507f1f77bcf86cd799439011")

        assert result is False
