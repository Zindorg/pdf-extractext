"""Interface for PDF repository (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List

from models.pdf_document import PDFDocument


class PDFRepositoryInterface(ABC):
    """Abstract interface for PDF repository."""

    @abstractmethod
    async def save(self, file_content: bytes, filename: str) -> Path:
        """
        Save PDF file and return its path.

        Args:
            file_content: Binary content of the PDF
            filename: Original filename

        Returns:
            Path where the file was saved
        """
        pass

    @abstractmethod
    async def get(self, file_id: str) -> Optional[Path]:
        """
        Get file path by ID.

        Args:
            file_id: Unique identifier

        Returns:
            Path to file or None if not found
        """
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """
        Delete file by ID.

        Args:
            file_id: Unique identifier

        Returns:
            True if deleted, False otherwise
        """
        pass

    @abstractmethod
    def create(self, document: PDFDocument) -> PDFDocument:
        """
        Create a new PDF document in storage.

        Args:
            document: PDFDocument to persist

        Returns:
            PDFDocument with assigned ID
        """
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """
        Find document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            PDFDocument or None if not found
        """
        pass

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """
        Find document by checksum.

        Args:
            checksum: SHA-256 checksum string

        Returns:
            PDFDocument or None if not found
        """
        pass

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """
        Find all documents.

        Returns:
            List of all PDFDocuments
        """
        pass

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """
        Delete document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass
