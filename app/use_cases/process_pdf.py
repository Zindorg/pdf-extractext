"""Use case for processing PDF upload and persisting text to MongoDB."""

from app.services.pdf_service import PDFService


class ProcessPDFFile:
    """Handle PDF upload, extract text, and persist to database."""

    def __init__(self, pdf_service: PDFService):
        """Initialize with PDF service."""
        self._pdf_service = pdf_service

    async def execute(self, file_content: bytes, filename: str):
        """Process PDF file and persist extracted text to database."""
        document = await self._pdf_service.process_pdf(file_content, filename)
        return document
