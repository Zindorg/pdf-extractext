"""PDF upload and validation operations."""

from app.config.settings import settings
from app.exceptions import InvalidFileException
from app.services.pdf_core import PDFCore
from app.services.pdf_extraction import PDFExtraction
from app.services.pdf_utils import validate_content, validate_filename, generate_checksum


class PDFUpload(PDFCore):
    """Service for handling PDF uploads."""

    async def process_upload(self, file_content: bytes, filename: str) -> dict:
        """
        Validate, process and persist a PDF upload.

        Returns:
            Dictionary with document data and duplicate flag.
        """
        validate_filename(filename)
        validate_content(file_content)

        if len(file_content) > settings.max_file_size:
            raise InvalidFileException("File too large")

        checksum = generate_checksum(file_content)
        existing = self._repository.find_by_checksum(checksum)

        if existing:
            return {
                "id": existing.id,
                "filename": existing.filename,
                "page_count": existing.page_count,
                "file_size": existing.file_size,
                "text_preview": existing.text_content[:500],
                "checksum": existing.checksum,
                "is_duplicate": True,
            }

        extraction = PDFExtraction(self._repository)
        doc = await extraction.process_pdf(file_content, filename)
        return {
            "id": doc.id,
            "filename": doc.filename,
            "page_count": doc.page_count,
            "file_size": doc.file_size,
            "text_preview": doc.text_content[:500],
            "checksum": doc.checksum,
            "is_duplicate": False,
        }
