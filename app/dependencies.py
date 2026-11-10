"""Composition root: wires adapters and configuration into the use cases.

This is the only module (besides main.py) that knows about concrete
infrastructure classes and about settings.
"""

from fastapi import Depends, Request
from pymongo.database import Database

from app.config.settings import settings
from app.domain.ports import PDFReader, PDFTextExtractor, PDFWriter
from app.infrastructure.mongo_pdf_repository import MongoPDFRepository
from app.infrastructure.pypdf_extractor import PypdfTextExtractor
from app.use_cases.delete_pdf import DeletePDF
from app.use_cases.get_pdf import GetPDF
from app.use_cases.list_pdfs import ListPDFs
from app.use_cases.upload_pdf import UploadPDF


def get_database(request: Request) -> Database:
    """MongoDB database opened in the application lifespan."""
    return request.app.state.mongodb_database


def get_pdf_repository(database: Database = Depends(get_database)) -> MongoPDFRepository:
    """Single adapter that implements both PDFReader and PDFWriter."""
    return MongoPDFRepository(database=database)


def get_text_extractor() -> PDFTextExtractor:
    return PypdfTextExtractor()


def get_upload_pdf_use_case(
    writer: PDFWriter = Depends(get_pdf_repository),
    extractor: PDFTextExtractor = Depends(get_text_extractor),
) -> UploadPDF:
    return UploadPDF(writer, extractor, max_file_size=settings.max_file_size)


def get_list_pdfs_use_case(reader: PDFReader = Depends(get_pdf_repository)) -> ListPDFs:
    return ListPDFs(reader)


def get_get_pdf_use_case(reader: PDFReader = Depends(get_pdf_repository)) -> GetPDF:
    return GetPDF(reader)


def get_delete_pdf_use_case(writer: PDFWriter = Depends(get_pdf_repository)) -> DeletePDF:
    return DeletePDF(writer)
