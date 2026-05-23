"""Use case for extracting text from a persisted PDF document."""

from app.schemas.pdf_schemas import PDFExtractResponse
from app.services.pdf_service import PDFService


class ExtractText:
    """Retrieve extracted text from a persisted PDF document."""

    def __init__(self, pdf_service: PDFService):
        """Initialize with PDF service.

        Args:
            pdf_service: Injected PDF service.
        """
        self._pdf_service = pdf_service

    def execute(self, file_id: str) -> PDFExtractResponse:
        """Retrieve extracted text from a persisted document.

        Args:
            file_id: Document ID.

        Returns:
            PDFExtractResponse with extracted text.
        """
        doc = self._pdf_service.get_persisted_document(file_id)

        return PDFExtractResponse(
            id=doc.id,
            filename=doc.filename,
            text=doc.text_content,
            pages_extracted=doc.page_count,
            total_pages=doc.page_count,
        )
