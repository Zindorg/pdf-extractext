"""Business logic service for PDF processing."""

from pathlib import Path

from models.pdf_document import PDFDocument
from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from services.interfaces.pdf_service_interface import PDFServiceInterface
from infrastructure import pdf_extractor
from core.exceptions import PDFExtractionException, InvalidFileException


def _validate_filename(filename: str) -> None:
    """Validate filename."""
    if not filename:
        raise InvalidFileException("Filename cannot be empty")
    if not filename.strip():
        raise InvalidFileException("Filename cannot be whitespace only")
    suffix = Path(filename).suffix.lower()
    if not suffix or suffix != ".pdf":
        raise InvalidFileException("File must be a PDF")


def _validate_content(file_content: bytes) -> None:
    """Validate file content."""
    if not file_content:
        raise InvalidFileException("File is empty")


class PDFService(PDFServiceInterface):
    """Service for PDF business operations."""

    def __init__(self, repository: PDFRepositoryInterface) -> None:
        """Initialize service with repository."""
        self._repository = repository

    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """
        Process a new PDF.

        Args:
            file_content: Binary PDF content
            filename: Original filename

        Returns:
            PDFDocument with extracted data

        Raises:
            InvalidFileException: If file is not valid
            PDFExtractionException: If extraction fails
        """
        _validate_filename(filename)
        _validate_content(file_content)

        try:
            text, page_count = pdf_extractor.extract_text(file_content)
            file_path = await self._repository.save(file_content, filename)

            return PDFDocument(
                id=file_path.stem.split("_")[0],
                filename=filename,
                file_size=len(file_content),
                page_count=page_count,
                text_content=text,
            )
        except InvalidFileException:
            raise
        except Exception as e:
            raise PDFExtractionException(f"Error processing PDF: {e}") from e

    async def extract_text_from_pdf(
        self, file_id: str, start_page: int = 1, end_page: int = 0
    ) -> PDFDocument:
        """
        Extract text from existing PDF with page range.

        Args:
            file_id: Unique identifier
            start_page: Starting page (1-indexed)
            end_page: Ending page (0 = all pages)

        Returns:
            PDFDocument with extracted text

        Raises:
            PDFExtractionException: If extraction fails
        """
        file_path = await self._repository.get(file_id)
        if not file_path or not file_path.exists():
            raise PDFExtractionException(f"PDF not found: {file_id}")

        try:
            content = file_path.read_bytes()
            text, pages_extracted = pdf_extractor.extract_text_from_page_range(
                content, start_page, end_page
            )

            return PDFDocument(
                id=file_id,
                filename=file_path.name.split("_", 1)[1],
                page_count=pages_extracted,
                text_content=text,
            )
        except Exception as e:
            raise PDFExtractionException(f"Error extracting text: {e}") from e
