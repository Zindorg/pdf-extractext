"""Command operations for PDF document modification."""

import logging

from app.services.pdf_core import PDFCore

logger = logging.getLogger(__name__)


class PDFCommands(PDFCore):
    """Service for modifying PDF document state."""

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete PDF document by ID."""
        logger.info("Permanently deleting document: %s", doc_id)
        return self._repository.delete_by_id(doc_id)
