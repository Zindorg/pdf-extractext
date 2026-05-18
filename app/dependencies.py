"""Dependency injection helpers for FastAPI application.

This module provides FastAPI-compatible dependency injection functions.
It serves as the wiring layer between infrastructure and the API layer.
"""

from typing import Generator

from app.repositories.repository_factory import RepositoryFactory
from app.services.pdf_service import PDFService


def get_pdf_service() -> PDFService:
    """Get configured PDF service instance."""
    repository = RepositoryFactory.get_pdf_repository()
    return PDFService(repository=repository)


def stream_text_response(text_content: str) -> Generator[bytes, None, None]:
    """Stream text content as bytes for HTTP response."""
    yield text_content.encode("utf-8")
