"""Utilidades compartidas para tests de API."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI

from app.api.exception_handlers import pdf_exception_handlers
from app.dependencies import (
    get_delete_pdf_use_case,
    get_download_text_use_case,
    get_extract_text_use_case,
    get_list_pdfs_use_case,
    get_process_pdf_use_case,
)
from app.models.pdf_document import PDFDocument
from app.routes.pdf_routes import router


from app.use_cases.delete_pdf import DeletePDF
from app.use_cases.download_text import DownloadExtractedText
from app.use_cases.extract_text import ExtractText
from app.use_cases.list_pdfs import ListPDFs
from app.use_cases.process_pdf import ProcessPDFFile


def _create_test_app(mock_extraction=None, mock_queries=None, mock_commands=None):
    app = FastAPI()

    # Default mock for queries if not provided
    if mock_queries is None:
        pdf_document = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123checksum",
            filename="document.pdf",
            page_count=5,
            file_size=1024,
            text_content="Extracted text",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_queries = MagicMock()
        mock_queries.find_by_id.return_value = pdf_document
        mock_queries.find_all.return_value = [pdf_document]
        mock_queries.get_persisted_document.return_value = pdf_document
    
    # Default mock for commands if not provided
    if mock_commands is None:
        mock_commands = MagicMock()
        mock_commands.delete_by_id.return_value = True

    # Default mock for extraction if not provided
    if mock_extraction is None:
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(return_value=PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123checksum",
            filename="document.pdf",
            page_count=5,
            file_size=1024,
            text_content="Extracted text",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ))

    # Create use cases from mocks
    list_uc = ListPDFs(mock_queries)
    extract_uc = ExtractText(mock_queries)
    delete_uc = DeletePDF(mock_commands)
    download_uc = DownloadExtractedText(mock_queries)
    process_uc = ProcessPDFFile(mock_extraction, mock_queries)

    app.dependency_overrides[get_list_pdfs_use_case] = lambda: list_uc
    app.dependency_overrides[get_extract_text_use_case] = lambda: extract_uc
    app.dependency_overrides[get_delete_pdf_use_case] = lambda: delete_uc
    app.dependency_overrides[get_download_text_use_case] = lambda: download_uc
    app.dependency_overrides[get_process_pdf_use_case] = lambda: process_uc

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
