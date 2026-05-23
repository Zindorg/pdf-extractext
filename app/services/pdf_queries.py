"""Query operations for PDF documents."""

from typing import List, Optional

from app.exceptions import PDFNotFoundException
from app.models.pdf_document import PDFDocument
from app.services.pdf_core import PDFCore


class PDFQueries(PDFCore):
    """Service for querying PDF documents data."""

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find PDF document by checksum."""
        return self._repository.find_by_checksum(checksum)

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find PDF document by ID."""
        return self._repository.find_by_id(doc_id)

    def find_all(self) -> List[PDFDocument]:
        """Find all PDF documents."""
        return self._repository.find_all()

    def get_persisted_document(self, doc_id: str) -> PDFDocument:
        """Get persisted PDF document by ID.

        Raises:
            PDFNotFoundException: If document not found.
        """
        doc = self._repository.find_by_id(doc_id)
        if doc is None:
            raise PDFNotFoundException(f"PDF not found: {doc_id}")
        return doc
