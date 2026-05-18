"""Use case for downloading extracted text as a .txt file."""

from typing import Generator

from app.exceptions import PDFNotFoundException
from app.services.pdf_service import PDFService


class DownloadExtractedText:
    """Retrieve extracted text and format for download as .txt file."""

    def __init__(self, pdf_service: PDFService):
        """Initialize with PDF service."""
        self._pdf_service = pdf_service

    def execute(self, doc_id: str) -> str:
        """Get formatted text for download from persisted document."""
        doc = self._pdf_service.get_persisted_document(doc_id)
        if doc is None or not doc.text_content:
            raise PDFNotFoundException(f"Document text not available: {doc_id}")
        return doc.text_content

    @staticmethod
    def stream_text(text_content: str) -> Generator[bytes, None, None]:
        """Stream text content as bytes for HTTP response."""
        yield text_content.encode("utf-8")
