"""Dependency injection helpers for FastAPI application.

This module provides FastAPI-compatible dependency injection functions.
It serves as the wiring layer between infrastructure and the API layer.
"""

from fastapi import Depends, Request

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from app.services.pdf_service import PDFService
from app.use_cases.delete_pdf import DeletePDF
from app.use_cases.download_text import DownloadExtractedText
from app.use_cases.extract_text import ExtractText
from app.use_cases.get_pdf import GetPDF
from app.use_cases.list_pdfs import ListPDFs


# --- Database dependency ---

def get_database(request: Request):
    """Get MongoDB database instance from app state."""
    return request.app.state.mongodb_database


# --- Repository dependency ---

def get_pdf_repository(database=Depends(get_database)):
    """Create PDF repository with injected database."""
    return MongoPDFRepository(database=database)


# --- Service dependency ---

def get_pdf_service(repository=Depends(get_pdf_repository)):
    """Create PDF service with injected repository."""
    return PDFService(repository=repository)


# --- Use case dependency injectors ---

def get_list_pdfs_use_case(service: PDFService = Depends(get_pdf_service)):
    """Inject ListPDFs use case."""
    return ListPDFs(service)


def get_get_pdf_use_case(service: PDFService = Depends(get_pdf_service)):
    """Inject GetPDF use case."""
    return GetPDF(service)


def get_extract_text_use_case(service: PDFService = Depends(get_pdf_service)):
    """Inject ExtractText use case."""
    return ExtractText(service)


def get_delete_pdf_use_case(service: PDFService = Depends(get_pdf_service)):
    """Inject DeletePDF use case."""
    return DeletePDF(service)


def get_download_text_use_case(service: PDFService = Depends(get_pdf_service)):
    """Inject DownloadExtractedText use case."""
    return DownloadExtractedText(service)
