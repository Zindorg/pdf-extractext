"""Command operations for PDF document modification."""

from typing import Optional

from app.models.pdf_document import PDFDocument
from app.services.pdf_core import PDFCore


class PDFCommands(PDFCore):
    """Service for modifying PDF document state."""

    def update_document(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document."""
        return self._repository.update(document)

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete PDF document by ID."""
        doc = self._repository.find_by_id(doc_id)
        if doc is None or doc.deleted_at is not None:
            return False
        return self._repository.soft_delete(doc_id)

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete PDF document by ID."""
        return self._repository.delete_by_id(doc_id)

    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted PDF document."""
        doc = self._repository.find_by_id(doc_id)
        if doc is None or doc.deleted_at is None:
            return False
        return self._repository.restore(doc_id)
