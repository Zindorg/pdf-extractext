"""Interface for PDF service (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.pdf_document import PDFDocument


class PDFServiceInterface(ABC):
    """Abstract interface for PDF service."""

    @abstractmethod
    def generate_checksum(self, file_content: bytes) -> str:
        """Generate SHA-256 checksum from file content."""
        pass

    @abstractmethod
    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process a PDF and extract its text."""
        pass

    @abstractmethod
    async def get_persisted_document(self, doc_id: str) -> PDFDocument:
        """Get an existing persisted PDF document."""
        pass

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find PDF document by ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """Find all PDF documents."""
        pass

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete PDF document by ID."""
        pass

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find PDF document by checksum."""
        pass
