"""Facade for PDF business operations.

This module provides a unified interface to PDF services. It delegates
to specialized modules for specific responsibilities.

Usage:
    service = PDFService(repository)
    await service.process_upload(content, filename)
    text = service.extract_text(content)
"""

from typing import List, Optional

from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.services.pdf_commands import PDFCommands
from app.services.pdf_extraction import PDFExtraction
from app.services.pdf_queries import PDFQueries
from app.services.pdf_upload import PDFUpload
from app.services.pdf_utils import generate_checksum


class PDFService:
    """Facade providing all PDF business operations."""

    def __init__(self, repository: PDFRepositoryInterface) -> None:
        """Initialize service with repository.

        Args:
            repository: PDF repository for data access.
        """
        self._repository = repository
        self._queries = PDFQueries(repository)
        self._commands = PDFCommands(repository)
        self._extraction = PDFExtraction(repository)
        self._upload = PDFUpload(repository)

    # --- Queries ---

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find PDF document by checksum."""
        return self._queries.find_by_checksum(checksum)

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find PDF document by ID."""
        return self._queries.find_by_id(doc_id)

    def find_all(self) -> List[PDFDocument]:
        """Find all PDF documents."""
        return self._queries.find_all()

    def get_persisted_document(self, doc_id: str) -> PDFDocument:
        """Get persisted PDF document by ID.

        Raises:
            PDFNotFoundException: If document not found.
        """
        return self._queries.get_persisted_document(doc_id)

    # --- Commands ---

    def update_document(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document."""
        return self._commands.update_document(document)

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete PDF document by ID."""
        return self._commands.soft_delete(doc_id)

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete PDF document by ID."""
        return self._commands.delete_by_id(doc_id)

    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted PDF document."""
        return self._commands.restore(doc_id)

    # --- Extraction ---

    def extract_text(self, file_content: bytes) -> str:
        """Extract text from PDF bytes and return it."""
        return self._extraction.extract_text(file_content)

    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process a new PDF and persist to MongoDB."""
        return await self._extraction.process_pdf(file_content, filename)

    # --- Upload ---

    async def process_upload(self, file_content: bytes, filename: str) -> dict:
        """
        Validate, process and persist a PDF upload.

        Returns a dictionary with document data and duplicate flag.
        """
        return await self._upload.process_upload(file_content, filename)

    # --- Utilities ---

    @staticmethod
    def generate_checksum(file_content: bytes) -> str:
        """Generate SHA-256 checksum from file content."""
        return generate_checksum(file_content)
