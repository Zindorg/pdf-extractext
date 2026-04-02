"""Interface for PDF service (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod

from models.pdf_document import PDFDocument


class PDFServiceInterface(ABC):
    """Abstract interface for PDF service."""

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
