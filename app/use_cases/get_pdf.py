"""Use case: get one persisted PDF (used by the text and download endpoints)."""

from app.domain.pdf_document import PDFDocument
from app.domain.ports import PDFRepository
from app.domain.exceptions import PDFNotFoundException


class GetPDF:
    """Return a persisted document or fail with 404."""

    def __init__(self, repository: PDFRepository) -> None:
        self._repository = repository

    def execute(self, doc_id: str) -> PDFDocument:
        """Raises PDFNotFoundException if the document does not exist."""
        document = self._repository.find_by_id(doc_id)
        if document is None:
            raise PDFNotFoundException(f"PDF not found: {doc_id}")
        return document
