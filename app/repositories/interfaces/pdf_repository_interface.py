"""Interface for PDF repository (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.pdf_document import PDFDocument


class PDFRepositoryInterface(ABC):
    """Abstract interface for PDF repository."""

    @abstractmethod
    def create(self, document: PDFDocument) -> PDFDocument:
        """Persist a new document and return it with its id.

        Raises:
            DuplicateDocumentException: If a document with the same checksum exists.
        """

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find a document by id; None if it does not exist or the id is invalid."""

    @abstractmethod
    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find a document by its SHA-256 checksum."""

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """Return all documents, newest first."""

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete a document; True if something was deleted."""