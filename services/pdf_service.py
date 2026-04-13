"""Business logic service for PDF processing."""

from models.pdf_document import PDFDocument
from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from services.interfaces.pdf_service_interface import PDFServiceInterface
from infrastructure.pdf_extractor_adapter import PDFExtractorAdapter
from core.exceptions import PDFExtractionException, InvalidFileException


class PDFService(PDFServiceInterface):
    """Service for PDF business operations."""

    def __init__(
        self,
        repository: PDFRepositoryInterface,
        extractor: PDFExtractorAdapter,
    ) -> None:
        """
        Initialize service with dependencies.

        Args:
            repository: Repository for file operations
            extractor: Adapter for text extraction
        """
        self._repository = repository
        self._extractor = extractor

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
        # Validate null inputs
        if filename is None:
            raise InvalidFileException("Filename cannot be null")

        if file_content is None:
            raise InvalidFileException("File content cannot be null")

        # Validate type
        if not isinstance(filename, str):
            raise InvalidFileException("Filename must be a string")

        # Validate empty inputs
        if filename.strip() == "":
            raise InvalidFileException("Filename cannot be empty")

        if len(file_content) == 0:
            raise InvalidFileException("File is empty")

        # Validate extension
        if not filename.endswith(".pdf"):
            raise InvalidFileException("File must be a PDF")

        try:
            # Extract text
            text, page_count = self._extractor.extract_text(file_content)

            # Save file
            file_path = await self._repository.save(file_content, filename)

            # Create document
            doc = PDFDocument(
                id=file_path.stem.split("_")[0],
                filename=filename,
                file_size=len(file_content),
                page_count=page_count,
                text_content=text,
            )

            return doc
        except Exception as e:
            raise PDFExtractionException(f"Error processing PDF: {str(e)}")

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
            with open(file_path, "rb") as f:
                content = f.read()

            # Extract text with range
            text, pages_extracted = self._extractor.extract_text_from_page_range(
                content, start_page, end_page
            )

            doc = PDFDocument(
                id=file_id,
                filename=file_path.name.split("_", 1)[1],
                page_count=pages_extracted,
                text_content=text,
            )

            return doc
        except Exception as e:
            raise PDFExtractionException(f"Error extracting text: {str(e)}")
