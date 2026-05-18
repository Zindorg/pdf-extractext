"""Business logic service for PDF processing."""

import hashlib
import re
from pathlib import Path
from typing import List, Optional

from app.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractionException,
)
from app.infrastructure import pdf_extractor
from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.repositories.repository_factory import RepositoryFactory
from app.services.interfaces.pdf_service_interface import PDFServiceInterface


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage."""
    base = Path(filename).stem
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    return sanitized[:50] or "document"


def _validate_filename(filename: str) -> None:
    """Validate filename format."""
    if not filename:
        raise InvalidFileException("Filename cannot be empty")
    if not filename.strip():
        raise InvalidFileException("Filename cannot be whitespace only")
    suffix = Path(filename).suffix.lower()
    if not suffix or suffix != ".pdf":
        raise InvalidFileException("File must be a PDF")


def _validate_content(file_content: bytes) -> None:
    """Validate file content is not empty."""
    if not file_content:
        raise InvalidFileException("File is empty")


class PDFService(PDFServiceInterface):
    """Service for PDF business operations."""

    def __init__(self, repository: PDFRepositoryInterface = None) -> None:
        """Initialize service with repository."""
        self._repository = repository or RepositoryFactory.get_pdf_repository()

    def generate_checksum(self, file_content: bytes) -> str:
        """Generate SHA-256 checksum from file content."""
        return hashlib.sha256(file_content).hexdigest()

    def extract_text(self, file_content: bytes) -> str:
        """Extract text from PDF bytes and return it."""
        try:
            text, _ = pdf_extractor.extract_text(file_content)
            return text
        except Exception as e:
            raise PDFExtractionException(f"Text extraction failed: {e}") from e

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find PDF document by checksum."""
        return self._repository.find_by_checksum(checksum)

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find PDF document by ID."""
        return self._repository.find_by_id(doc_id)

    def find_all(self) -> List[PDFDocument]:
        """Find all PDF documents."""
        return self._repository.find_all()

    def update_document(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document."""
        return self._repository.update(document)

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete PDF document by ID."""
        doc = self._repository.find_by_id(doc_id)
        if doc is None or doc.deleted_at is not None:
            return False
        return self._repository.soft_delete(doc_id)

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete PDF document by ID."""
        return self._repository.delete_by_id(doc_id)

    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted PDF document."""
        doc = self._repository.find_by_id(doc_id)
        if doc is None or doc.deleted_at is None:
            return False
        return self._repository.restore(doc_id)

    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process a new PDF and persist to MongoDB."""
        _validate_filename(filename)
        _validate_content(file_content)

        try:
            checksum = self.generate_checksum(file_content)
            existing = self.find_by_checksum(checksum)
            if existing:
                raise DuplicateDocumentException(
                    f"Document with checksum {checksum} already exists",
                    existing_id=existing.id,
                )

            text, page_count = pdf_extractor.extract_text(file_content)

            if not text or not text.strip():
                raise PDFExtractionException("No text content extracted from PDF")

            document = PDFDocument(
                checksum=checksum,
                filename=filename,
                file_size=len(file_content),
                page_count=page_count,
                text_content=text,
            )

            return self._repository.create(document)

        except (InvalidFileException, DuplicateDocumentException):
            raise
        except Exception as e:
            raise PDFExtractionException(f"Error processing PDF: {e}") from e

    async def get_persisted_document(self, doc_id: str) -> Optional[PDFDocument]:
        """Get persisted PDF document by ID."""
        from app.exceptions import PDFNotFoundException
        doc = self._repository.find_by_id(doc_id)
        if doc is None:
            raise PDFNotFoundException(f"PDF not found: {doc_id}")
        return doc
