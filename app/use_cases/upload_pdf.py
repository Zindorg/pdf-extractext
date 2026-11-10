"""Use case: upload a PDF, extract its text and persist it."""

import logging

from app.domain.pdf_document import PDFDocument
from app.domain.ports import PDFTextExtractor, PDFWriter
from app.domain.uploaded_file import UploadedFile

logger = logging.getLogger(__name__)


class UploadPDF:
    """Validate, extract and persist an uploaded PDF."""

    def __init__(self, writer: PDFWriter, extractor: PDFTextExtractor, max_file_size: int) -> None:
        self._writer = writer
        self._extractor = extractor
        self._max_file_size = max_file_size

    def execute(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process an uploaded file.

        Raises:
            InvalidFileException: Bad name, empty or too large file.
            PDFExtractionException: Unreadable PDF or PDF without text.
            DuplicateDocumentException: Same content was already uploaded.
        """
        file = UploadedFile(filename=filename, content=file_content)
        file.ensure_not_larger_than(self._max_file_size)

        extracted = self._extractor.extract(file.content)
        document = self._writer.create(
            PDFDocument.from_upload(file, extracted.text, extracted.page_count)
        )
        logger.info("PDF uploaded: %s (id: %s)", filename, document.id)
        return document
