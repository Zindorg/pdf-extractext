"""Tests para sanitize_filename - elimina extension."""

from app.services.pdf_utils import sanitize_filename


class TestSanitizeFilenameRemovesPdfExtension:
    """Elimina extension .pdf."""

    def test_removes_extension(self):
        assert not sanitize_filename("document.pdf").endswith(".pdf")
