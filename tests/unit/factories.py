"""Builders centralizados para datos de prueba."""

from app.domain.pdf_document import PDFDocument


def make_pdf_document(**overrides) -> PDFDocument:
    """Crea un PDFDocument sin id, con valores por defecto sobrescribibles."""
    defaults = {
        "checksum": "abc123checksum",
        "filename": "test.pdf",
        "text_content": "sample content",
        "page_count": 5,
        "file_size": 1024,
    }
    defaults.update(overrides)
    return PDFDocument(**defaults)
