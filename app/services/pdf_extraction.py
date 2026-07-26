"""PDF text extraction operations."""

import logging

from app.config.settings import settings
from app.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractionException,
)
from app.infrastructure import pdf_extractor
from app.models.pdf_document import PDFDocument
from app.services.pdf_core import PDFCore
from app.services.pdf_utils import validate_content, validate_filename, generate_checksum

logger = logging.getLogger(__name__)


class PDFExtraction(PDFCore):
    """Service for extracting text from PDF documents."""

    def extract_text(self, file_content: bytes) -> str:
        """Extract text from PDF bytes and return it."""
        logger.debug("Extracting text from PDF content (%d bytes)", len(file_content))
        try:
            text, _page_count = pdf_extractor.extract_text(file_content)
            logger.debug("Text extraction successful (%d chars)", len(text))
            return text
        except Exception as e:
            logger.error("Text extraction failed: %s", e)
            raise PDFExtractionException(f"Text extraction failed: {e}") from e

    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process a new PDF and persist to MongoDB."""
        logger.debug("Processing PDF: %s (%d bytes)", filename, len(file_content))
        validate_filename(filename)
        validate_content(file_content)

        try:
            checksum = generate_checksum(file_content)
            existing = self._repository.find_by_checksum(checksum)
            if existing:
                logger.warning("Duplicate document detected: %s (checksum: %s)", filename, checksum)
                raise DuplicateDocumentException(
                    f"Document with checksum {checksum} already exists",
                    existing_id=existing.id,
                )

            text, page_count = pdf_extractor.extract_text(file_content)

            if not text or not text.strip():
                logger.warning("No text content extracted from PDF: %s", filename)
                raise PDFExtractionException("No text content extracted from PDF")

            document = PDFDocument(
                checksum=checksum,
                filename=filename,
                file_size=len(file_content),
                page_count=page_count,
                text_content=text,
            )

            created = self._repository.create(document)
            logger.debug("PDF created successfully: %s (id: %s)", filename, created.id)
            return created

        except (InvalidFileException, DuplicateDocumentException):
            raise
        except Exception as e:
            logger.error("Error processing PDF %s: %s", filename, e)
            raise PDFExtractionException(f"Error processing PDF: {e}") from e
