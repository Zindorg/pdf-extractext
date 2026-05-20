"""Utilidades compartidas para tests de API."""

from datetime import datetime

from app.models.pdf_document import PDFDocument
from app.exceptions import PDFNotFoundException

from app.routes.pdf_routes import get_pdf_service, router

from fastapi import FastAPI, HTTPException

def _create_test_app(mock_service=None):
    app = FastAPI()
    if mock_service:
        app.dependency_overrides[get_pdf_service] = lambda: mock_service
    app.include_router(router)

    @app.exception_handler(PDFNotFoundException)
    async def pdf_not_found_handler(request, exc):
        raise HTTPException(status_code=404, detail=str(exc))

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
