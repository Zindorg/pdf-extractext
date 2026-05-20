"""Tests para _sanitize_filename - elimina extension."""

from app.services.pdf_service import _sanitize_filename


class TestSanitizeFilenameRemovesPdfExtension:
    """Elimina extension .pdf."""

    def test_removes_extension(self):
        assert not _sanitize_filename("document.pdf").endswith(".pdf")
