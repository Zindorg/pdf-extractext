"""Use case for deleting a PDF document."""

from app.services.pdf_service import PDFService


class DeletePDF:
    """Handle PDF document deletion."""

    def __init__(self, pdf_service: PDFService):
        """Initialize with PDF service.

        Args:
            pdf_service: Injected PDF service.
        """
        self._pdf_service = pdf_service

    def execute(self, doc_id: str) -> bool:
        """Permanently delete a PDF document by ID.

        Args:
            doc_id: Document ID.

        Returns:
            True if deleted, False otherwise.
        """
        return self._pdf_service.delete_by_id(doc_id)
