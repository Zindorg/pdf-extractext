"""Use case: permanently delete a PDF."""

import logging

from app.domain.ports import PDFRepository
from app.domain.exceptions import PDFNotFoundException

logger = logging.getLogger(__name__)


class DeletePDF:
    """Delete a persisted document or fail with 404."""

    def __init__(self, repository: PDFRepository) -> None:
        self._repository = repository

    def execute(self, doc_id: str) -> None:
        """Raises PDFNotFoundException if the document does not exist."""
        if not self._repository.delete_by_id(doc_id):
            raise PDFNotFoundException(f"Document not found: {doc_id}")
        logger.info("PDF deleted: %s", doc_id)
