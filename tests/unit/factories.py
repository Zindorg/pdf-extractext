"""Builders centralizados para datos de prueba."""

from datetime import datetime

from bson import ObjectId

from app.models.pdf_document import PDFDocument

SAMPLE_OBJECT_ID = ObjectId("507f1f77bcf86cd799439011")
SAMPLE_CHECKSUM = "abc123checksum"


def make_pdf_document(**overrides) -> PDFDocument:
    """Crea un PDFDocument con valores por defecto, sobrescribibles."""
    defaults = {
        "id": str(SAMPLE_OBJECT_ID),
        "checksum": SAMPLE_CHECKSUM,
        "filename": "test.pdf",
        "text_content": "sample content",
        "page_count": 5,
        "file_size": 1024,
        "content_type": "application/pdf",
    }
    defaults.update(overrides)
    return PDFDocument(**defaults)


def make_mongo_doc(**overrides) -> dict:
    """Crea un dict con el formato de documento MongoDB."""
    now = datetime.now()
    defaults = {
        "_id": SAMPLE_OBJECT_ID,
        "checksum": SAMPLE_CHECKSUM,
        "filename": "test.pdf",
        "text_content": "content",
        "page_count": 1,
        "file_size": 100,
        "deleted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return defaults
