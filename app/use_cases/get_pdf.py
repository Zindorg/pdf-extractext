"""Use case for retrieving a single PDF document by ID."""

from typing import Optional

from app.models.pdf_document import PDFDocument
from app.schemas.pdf_schemas import PDFDetailResponse
from app.services.pdf_queries import PDFQueries


class GetPDF:
    """Retrieve a single PDF document by ID."""

    def __init__(self, queries: PDFQueries) -> None:
        """Initialize with queries service.

        Args:
            queries: Injected PDF queries service.
        """
        self._queries = queries

    def execute(self, doc_id: str) -> Optional[PDFDetailResponse]:
        """Retrieve PDF by ID and map to response schema.

        Args:
            doc_id: PDF document ID.

        Returns:
            PDFDetailResponse if found, None otherwise.
        """
        doc: Optional[PDFDocument] = self._queries.find_by_id(doc_id)

        if doc is None:
            return None

        return PDFDetailResponse(
            id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count,
            file_size=doc.file_size,
            checksum=doc.checksum,
            text_content=doc.text_content,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
