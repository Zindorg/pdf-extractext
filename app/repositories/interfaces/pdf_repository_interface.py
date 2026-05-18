"""Interface for PDF repository (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.pdf_document import PDFDocument


class PDFRepositoryInterface(ABC):
    """Abstract interface for PDF repository."""

    @abstractmethod
    def create(self, document: PDFDocument) -> PDFDocument:
        """Create a new PDF document in storage."""
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find active document by ID."""
        pass

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find active document by checksum."""
        pass

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """Find all active (non-deleted) documents."""
        pass

    @abstractmethod
    def update(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document."""
        pass

    @abstractmethod
    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete document by ID."""
        pass

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete document by ID."""
        pass

    @abstractmethod
    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted document."""
        pass
