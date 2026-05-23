"""Utilidades compartidas para tests de API."""

from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI

from app.api.exception_handlers import pdf_exception_handlers
from app.dependencies import (
    get_delete_pdf_use_case,
    get_download_text_use_case,
    get_extract_text_use_case,
    get_get_pdf_use_case,
    get_list_pdfs_use_case,
    get_pdf_service,
)
from app.models.pdf_document import PDFDocument
from app.routes.pdf_routes import router


def _create_test_app(mock_service=None):
    app = FastAPI()

    if mock_service is not None:
        # Inyectar el servicio mock en el endpoint de upload
        app.dependency_overrides[get_pdf_service] = lambda: mock_service

        # Generar mocks de los use cases para otros endpoints
        from app.use_cases.delete_pdf import DeletePDF
        from app.use_cases.download_text import DownloadExtractedText
        from app.use_cases.extract_text import ExtractText
        from app.use_cases.get_pdf import GetPDF
        from app.use_cases.list_pdfs import ListPDFs

        pdf_document = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123checksum",
            filename="document.pdf",
            page_count=5,
            file_size=1024,
            text_content="Extracted text",
        )

        list_uc = MagicMock(spec=ListPDFs)
        list_uc.execute.return_value = MagicMock(
            documents=[pdf_document], total=1
        )

        get_uc = MagicMock(spec=GetPDF)
        get_uc.execute.return_value = pdf_document

        extract_uc = MagicMock(spec=ExtractText)
        extract_uc.execute.return_value = MagicMock(
            id=pdf_document.id,
            filename=pdf_document.filename,
            text=pdf_document.text_content,
            pages_extracted=pdf_document.page_count,
            total_pages=pdf_document.page_count,
        )

        delete_uc = MagicMock(spec=DeletePDF)
        delete_uc.execute.return_value = True

        download_uc = MagicMock(spec=DownloadExtractedText)
        download_uc.execute.return_value = pdf_document.text_content

        app.dependency_overrides[get_list_pdfs_use_case] = lambda: list_uc
        app.dependency_overrides[get_get_pdf_use_case] = lambda: get_uc
        app.dependency_overrides[get_extract_text_use_case] = lambda: extract_uc
        app.dependency_overrides[get_delete_pdf_use_case] = lambda: delete_uc
        app.dependency_overrides[get_download_text_use_case] = lambda: download_uc

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
