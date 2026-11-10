"""Use case: upload a PDF, extract its text and persist it."""

import logging

from app.domain.pdf_document import PDFDocument
from app.domain.pdf_rules import (
    generate_checksum,
    validate_content,
    validate_filename,
    validate_size,
)
from app.domain.ports import PDFRepository, PDFTextExtractor
from app.exceptions import DuplicateDocumentException, PDFExtractionException

logger = logging.getLogger(__name__)


class UploadPDF:
    """Validate, deduplicate, extract and persist an uploaded PDF."""

    def __init__(
        self, repository: PDFRepository, extractor: PDFTextExtractor, max_file_size: int
    ) -> None:
        self._repository = repository
        self._extractor = extractor
        self._max_file_size = max_file_size

    def execute(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process an uploaded file.

        Raises:
            InvalidFileException: Bad name, empty or too large file.
            DuplicateDocumentException: Same content was already uploaded.
            PDFExtractionException: Unreadable PDF or PDF without text.
        """
        validate_filename(filename)
        validate_content(file_content)
        validate_size(file_content, self._max_file_size)

        checksum = generate_checksum(file_content)
        existing = self._repository.find_by_checksum(checksum)
        if existing:
            raise DuplicateDocumentException(
                f"Document with checksum {checksum} already exists",
                existing_id=existing.id,
            )

        extracted = self._extractor.extract(file_content)
        if not extracted.text:
            raise PDFExtractionException("No text content extracted from PDF")

        document = self._repository.create(
            PDFDocument(
                checksum=checksum,
                filename=filename,
                file_size=len(file_content),
                page_count=extracted.page_count,
                text_content=extracted.text,
            )
        )
        logger.info("PDF uploaded: %s (id: %s)", filename, document.id)
        return document
