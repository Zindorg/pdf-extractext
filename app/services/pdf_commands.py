"""Command operations for PDF document modification."""

import logging
from typing import Optional

from app.models.pdf_document import PDFDocument
from app.services.pdf_core import PDFCore

logger = logging.getLogger(__name__)


class PDFCommands(PDFCore):
    """Service for modifying PDF document state."""

    def update_document(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document."""
        logger.info("Updating document: %s", document.id)
        return self._repository.update(document)

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete PDF document by ID."""
        doc = self._repository.find_by_id(doc_id)
        if doc is None or doc.deleted_at is not None:
            logger.warning("Soft delete failed: document not found or already deleted: %s", doc_id)
            return False
        logger.info("Soft deleting document: %s", doc_id)
        return self._repository.soft_delete(doc_id)

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete PDF document by ID."""
        logger.info("Permanently deleting document: %s", doc_id)
        return self._repository.delete_by_id(doc_id)

    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted PDF document."""
        doc = self._repository.find_by_id(doc_id)
        if doc is None or doc.deleted_at is None:
            logger.warning("Restore failed: document not found or not deleted: %s", doc_id)
            return False
        logger.info("Restoring document: %s", doc_id)
        return self._repository.restore(doc_id)
