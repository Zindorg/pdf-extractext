"""Query operations for PDF documents."""

import logging
from typing import List, Optional

from app.exceptions import PDFNotFoundException
from app.models.pdf_document import PDFDocument
from app.services.pdf_core import PDFCore

logger = logging.getLogger(__name__)


class PDFQueries(PDFCore):
    """Service for querying PDF documents data."""

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find PDF document by checksum."""
        logger.debug("Finding document by checksum: %s", checksum)
        return self._repository.find_by_checksum(checksum)

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find PDF document by ID."""
        logger.debug("Finding document by id: %s", doc_id)
        return self._repository.find_by_id(doc_id)

    def find_all(self) -> List[PDFDocument]:
        """Find all PDF documents."""
        logger.debug("Retrieving all PDF documents")
        return self._repository.find_all()

    def get_persisted_document(self, doc_id: str) -> PDFDocument:
        """Get persisted PDF document by ID.

        Raises:
            PDFNotFoundException: If document not found.
        """
        doc = self._repository.find_by_id(doc_id)
        if doc is None:
            logger.warning("Document not found: %s", doc_id)
            raise PDFNotFoundException(f"PDF not found: {doc_id}")
        logger.debug("Document found: %s", doc_id)
        return doc
