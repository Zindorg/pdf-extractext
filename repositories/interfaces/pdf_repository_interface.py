"""Interface for PDF repository (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from models.pdf_document import PDFDocument


class PDFRepositoryInterface(ABC):
    """Abstract interface for PDF repository.

    Define el contrato que deben implementar todos los repositorios
    de documentos PDF. Sigue el Principio de Inversión de Dependencias.

    Implementaciones:
        - MongoPDFRepository: Persistencia en MongoDB.

    Example:
        >>> class MyRepository(PDFRepositoryInterface):
        ...     def create(self, document: PDFDocument) -> PDFDocument:
        ...         ...
    """

    @abstractmethod
    def create(self, document: PDFDocument) -> PDFDocument:
        """Create a new PDF document in storage.

        Args:
            document: PDFDocument to persist.

        Returns:
            PDFDocument with assigned ID.
        """
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find active document by ID.

        Args:
            doc_id: Document unique identifier.

        Returns:
            PDFDocument or None if not found.
        """
        pass

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find active document by checksum.

        Args:
            checksum: SHA-256 checksum string.

        Returns:
            PDFDocument or None if not found.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """Find all active (non-deleted) documents.

        Returns:
            List of active PDFDocuments.
        """
        pass

    @abstractmethod
    def update(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document.

        Args:
            document: PDFDocument with updated fields.

        Returns:
            Updated PDFDocument or None if not found.
        """
        pass

    @abstractmethod
    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete document by ID.

        Args:
            doc_id: Document unique identifier.

        Returns:
            True if marked as deleted, False if not found.
        """
        pass

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete document by ID.

        Args:
            doc_id: Document unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted document.

        Args:
            doc_id: Document unique identifier.

        Returns:
            True if restored, False if not found.
        """
        pass
