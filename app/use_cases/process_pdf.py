"""Use case for processing PDF upload and persisting text to MongoDB."""

import logging
from typing import Any

from app.services.pdf_extraction import PDFExtraction
from app.services.pdf_queries import PDFQueries

logger = logging.getLogger(__name__)


class ProcessPDFFile:
    """Handle PDF upload, extract text, and persist to database."""

    def __init__(self, extraction: PDFExtraction, queries: PDFQueries) -> None:
        """Initialize with specialized services.

        Args:
            extraction: PDF extraction service.
            queries: PDF queries service for persistence checks.
        """
        self._extraction = extraction
        self._queries = queries

    async def execute(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """Process PDF file, extract text, persist to database, and return DTO."""
        logger.debug("Processing uploaded file: %s", filename)
        document = await self._extraction.process_pdf(file_content, filename)

        return {
            "id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "file_size": document.file_size,
            "text_preview": document.text_content[:500],
            "checksum": document.checksum,
            "is_duplicate": False,
        }
