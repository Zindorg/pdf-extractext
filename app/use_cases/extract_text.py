"""Use case for extracting text from a persisted PDF document."""

from app.schemas.pdf_schemas import PDFExtractResponse
from app.services.pdf_queries import PDFQueries


class ExtractText:
    """Retrieve extracted text from a persisted PDF document."""

    def __init__(self, queries: PDFQueries):
        """Initialize with queries service.

        Args:
            queries: Injected PDF queries service.
        """
        self._queries = queries

    def execute(self, file_id: str) -> PDFExtractResponse:
        """Retrieve extracted text from a persisted document.

        Args:
            file_id: Document ID.

        Returns:
            PDFExtractResponse with extracted text.
        """
        doc = self._queries.get_persisted_document(file_id)

        return PDFExtractResponse(
            id=doc.id,
            filename=doc.filename,
            text=doc.text_content,
            pages_extracted=doc.page_count,
            total_pages=doc.page_count,
        )
