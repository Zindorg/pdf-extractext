"""Dependency injection helpers for FastAPI application.

This module provides FastAPI-compatible dependency injection functions.
It acts as the wiring layer between infrastructure and the API layer,
connecting concrete implementations without exposing them to consumers.
"""

from fastapi import Depends, Request

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from app.services.pdf_commands import PDFCommands
from app.services.pdf_extraction import PDFExtraction
from app.services.pdf_queries import PDFQueries
from app.use_cases.delete_pdf import DeletePDF
from app.use_cases.download_text import DownloadExtractedText
from app.use_cases.extract_text import ExtractText
from app.use_cases.list_pdfs import ListPDFs
from app.use_cases.process_pdf import ProcessPDFFile


# --- Database dependency ---

def get_database(request: Request):
    """Get MongoDB database instance from app state."""
    return request.app.state.mongodb_database


# --- Repository dependency ---

def get_pdf_repository(database=Depends(get_database)):
    """Create PDF repository with injected database."""
    return MongoPDFRepository(database=database)


# --- Service dependencies ---

def get_pdf_queries(repository=Depends(get_pdf_repository)):
    """Create PDF queries service with injected repository."""
    return PDFQueries(repository=repository)


def get_pdf_extraction(repository=Depends(get_pdf_repository)):
    """Create PDF extraction service with injected repository."""
    return PDFExtraction(repository=repository)


def get_pdf_commands(repository=Depends(get_pdf_repository)):
    """Create PDF commands service with injected repository."""
    return PDFCommands(repository=repository)


# --- Use case dependency injectors ---

def get_list_pdfs_use_case(queries=Depends(get_pdf_queries)):
    """Inject ListPDFs use case."""
    return ListPDFs(queries)


def get_extract_text_use_case(queries=Depends(get_pdf_queries)):
    """Inject ExtractText use case."""
    return ExtractText(queries)


def get_delete_pdf_use_case(commands=Depends(get_pdf_commands)):
    """Inject DeletePDF use case."""
    return DeletePDF(commands)


def get_download_text_use_case(queries=Depends(get_pdf_queries)):
    """Inject DownloadExtractedText use case."""
    return DownloadExtractedText(queries)


def get_process_pdf_use_case(
    extraction=Depends(get_pdf_extraction),
    queries=Depends(get_pdf_queries),
):
    """Inject ProcessPDFFile use case."""
    return ProcessPDFFile(extraction, queries)
