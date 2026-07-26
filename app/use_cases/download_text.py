"""Use case for downloading extracted text as a .txt file."""

import logging
from typing import Generator

from app.exceptions import PDFNotFoundException
from app.models.pdf_document import PDFDocument
from app.services.pdf_queries import PDFQueries

logger = logging.getLogger(__name__)


class DownloadExtractedText:
    """Retrieve extracted text and format for download as .txt file."""

    def __init__(self, queries: PDFQueries):
        """Initialize with queries service.

        Args:
            queries: Injected PDF queries service.
        """
        self._queries = queries

    def execute(self, doc_id: str) -> PDFDocument:
        """Get persisted document for download.

        Args:
            doc_id: Document ID.

        Returns:
            PDFDocument with text content.
        """
        logger.debug("Downloading text for document: %s", doc_id)
        doc = self._queries.get_persisted_document(doc_id)
        if doc is None or not doc.text_content:
            logger.warning("Document text not available: %s", doc_id)
            raise PDFNotFoundException(f"Document text not available: {doc_id}")
        return doc

    @staticmethod
    def stream_text(text_content: str) -> Generator[bytes, None, None]:
        """Stream text content as bytes for HTTP response."""
        logger.debug("Streaming text content (%d chars)", len(text_content))
        yield text_content.encode("utf-8")
