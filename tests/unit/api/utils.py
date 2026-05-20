"""Utilidades compartidas para tests de API."""

from datetime import datetime

from fastapi import FastAPI

from app.api.exception_handlers import pdf_exception_handlers
from app.routes.pdf_routes import get_pdf_service, router
from app.models.pdf_document import PDFDocument


def _create_test_app(mock_service=None):
    app = FastAPI()
    if mock_service:
        app.dependency_overrides[get_pdf_service] = lambda: mock_service

    # Register RFC 9457 exception handlers
    for exc_class, handler in pdf_exception_handlers.items():
        app.add_exception_handler(exc_class, handler)

    app.include_router(router)
    return app


def _make_document(**overrides):
    """Crea un PDFDocument con valores por defecto."""
    defaults = dict(
        id="507f1f77bcf86cd799439011",
        checksum="abc123checksum",
        filename="document.pdf",
        text_content="Extracted text",
        page_count=5,
        file_size=1024,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    defaults.update(overrides)
    return PDFDocument(**defaults)
