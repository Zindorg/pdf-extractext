"""PDF text extraction operations."""

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


class PDFExtraction(PDFCore):
    """Service for extracting text from PDF documents."""

    def extract_text(self, file_content: bytes) -> str:
        """Extract text from PDF bytes and return it."""
        try:
            text, _page_count = pdf_extractor.extract_text(file_content)
            return text
        except Exception as e:
            raise PDFExtractionException(f"Text extraction failed: {e}") from e

    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process a new PDF and persist to MongoDB."""
        validate_filename(filename)
        validate_content(file_content)

        try:
            checksum = generate_checksum(file_content)
            existing = self._repository.find_by_checksum(checksum)
            if existing:
                raise DuplicateDocumentException(
                    f"Document with checksum {checksum} already exists",
                    existing_id=existing.id,
                )

            text, page_count = pdf_extractor.extract_text(file_content)

            if not text or not text.strip():
                raise PDFExtractionException("No text content extracted from PDF")

            document = PDFDocument(
                checksum=checksum,
                filename=filename,
                file_size=len(file_content),
                page_count=page_count,
                text_content=text,
            )

            return self._repository.create(document)

        except (InvalidFileException, DuplicateDocumentException):
            raise
        except Exception as e:
            raise PDFExtractionException(f"Error processing PDF: {e}") from e
