"""Interface for PDF service (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from models.pdf_document import PDFDocument


class PDFServiceInterface(ABC):
    """Abstract interface for PDF service."""

    @abstractmethod
    def generate_checksum(self, file_content: bytes) -> str:
        """
        Generate SHA-256 checksum from file content.

        Args:
            file_content: Binary file content

        Returns:
            Hexadecimal checksum string
        """
        pass

    @abstractmethod
    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """
        Process a PDF and extract its text.

        Args:
            file_content: Binary content of the PDF
            filename: Original filename

        Returns:
            PDFDocument with extracted data
        """
        pass

    @abstractmethod
    async def extract_text_from_pdf(
        self, file_id: str, start_page: int = 1, end_page: int = 0
    ) -> PDFDocument:
        """
        Extract text from an existing PDF.

        Args:
            file_id: Unique identifier
            start_page: Starting page (1-indexed)
            end_page: Ending page (0 = all pages)

        Returns:
            PDFDocument with extracted text
        """
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """
        Find PDF document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            PDFDocument or None if not found
        """
        pass

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """
        Find all PDF documents.

        Returns:
            List of all PDFDocuments
        """
        pass

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """
        Delete PDF document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """
        Find PDF document by checksum.

        Args:
            checksum: SHA-256 checksum string

        Returns:
            PDFDocument or None if not found
        """
        pass
