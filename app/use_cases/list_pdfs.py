"""Use case for listing all PDF documents."""

from typing import List

from app.models.pdf_document import PDFDocument
from app.schemas.pdf_schemas import PDFDocumentResponse, PDFListResponse
from app.services.pdf_queries import PDFQueries


class ListPDFs:
    """Retrieve all persisted PDF documents."""

    def __init__(self, queries: PDFQueries):
        """Initialize with queries service.

        Args:
            queries: Injected PDF queries service.
        """
        self._queries = queries

    def execute(self) -> PDFListResponse:
        """Retrieve all PDFs and map to response schema.

        Returns:
            PDFListResponse with list of documents and total count.
        """
        documents: List[PDFDocument] = self._queries.find_all()

        doc_responses = [
            PDFDocumentResponse(
                id=doc.id,
                filename=doc.filename,
                page_count=doc.page_count,
                file_size=doc.file_size,
                checksum=doc.checksum,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ]

        return PDFListResponse(documents=doc_responses, total=len(doc_responses))
