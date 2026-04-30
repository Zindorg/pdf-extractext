"""Business logic service for PDF processing."""

import hashlib
import re
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from app.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractionException,
    PDFNotFoundException,
)
from app.infrastructure import pdf_extractor
from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.repositories.repository_factory import RepositoryFactory
from app.services.interfaces.pdf_service_interface import PDFServiceInterface


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for temporary file creation.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename without extension
    """
    base = Path(filename).stem
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    return sanitized[:50] or "document"


def _validate_filename(filename: str) -> None:
    """Validate filename.

    Args:
        filename: Filename to validate

    Raises:
        InvalidFileException: If filename is invalid
    """
    if not filename:
        raise InvalidFileException("Filename cannot be empty")
    if not filename.strip():
        raise InvalidFileException("Filename cannot be whitespace only")
    suffix = Path(filename).suffix.lower()
    if not suffix or suffix != ".pdf":
        raise InvalidFileException("File must be a PDF")


def _validate_content(file_content: bytes) -> None:
    """Validate file content.

    Args:
        file_content: Binary content to validate

    Raises:
        InvalidFileException: If content is invalid
    """
    if not file_content:
        raise InvalidFileException("File is empty")


class PDFService(PDFServiceInterface):
    """Service for PDF business operations.

    Orquesta las operaciones de negocio relacionadas con PDFs,
    incluyendo extracción de texto, validación de duplicados
    y persistencia en MongoDB.

    Attributes:
        _repository: Repositorio para operaciones CRUD.
        _last_extracted_text: Último texto extraído (para debugging).
        _last_temp_path: Última ruta de archivo temporal.

    Example:
        >>> service = PDFService()
        >>> doc = await service.process_pdf(content, "file.pdf")
    """

    def __init__(self, repository: PDFRepositoryInterface = None) -> None:
        """Initialize service with repository.

        Args:
            repository: Repository instance. If None, uses factory.
        """
        self._repository = repository or RepositoryFactory.get_pdf_repository()
        self._last_extracted_text: str = ""
        self._last_temp_path: Path | None = None

    def generate_checksum(self, file_content: bytes) -> str:
        """Generate SHA-256 checksum from file content.

        Args:
            file_content: Binary file content

        Returns:
            Hexadecimal checksum string
        """
        return hashlib.sha256(file_content).hexdigest()

    def generate_text_file(self, file_content: bytes, filename: str) -> Tuple[str, Path]:
        """Extract text from PDF bytes and create temporary .txt file.

        Args:
            file_content: Binary PDF content
            filename: Original filename for naming the .txt

        Returns:
            Tuple of (extracted text, path to temporary .txt file)

        Raises:
            InvalidFileException: If input is invalid
            PDFExtractionException: If extraction fails

        Note:
            PDF content is processed in memory only and NOT persisted.
            The caller is responsible for cleaning up the temporary file.
        """
        if not file_content:
            raise InvalidFileException("File content is empty")
        if not filename:
            raise InvalidFileException("Filename is empty")

        try:
            text, _ = pdf_extractor.extract_text(file_content)
        except Exception as e:
            raise PDFExtractionException(f"Text extraction failed: {e}") from e

        self._last_extracted_text = text

        base_name = _sanitize_filename(filename)
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            prefix=f"{base_name}_",
            delete=False,
            encoding="utf-8",
        ) as tmp_file:
            tmp_file.write(text)
            self._last_temp_path = Path(tmp_file.name)

        return text, self._last_temp_path

    def cleanup_memory(self) -> None:
        """Clear internal memory references after processing.

        Note:
            This does NOT delete temporary files. The webapp
            is responsible for managing file lifecycle.
        """
        self._last_extracted_text = ""
        self._last_temp_path = None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find PDF document by checksum.

        Args:
            checksum: SHA-256 checksum string

        Returns:
            PDFDocument or None if not found
        """
        return self._repository.find_by_checksum(checksum)

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find PDF document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            PDFDocument or None if not found
        """
        return self._repository.find_by_id(doc_id)

    def find_all(self) -> List[PDFDocument]:
        """Find all PDF documents.

        Returns:
            List of all non-deleted PDFDocuments
        """
        return self._repository.find_all()

    def update_document(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document.

        Args:
            document: PDFDocument with updated fields

        Returns:
            Updated PDFDocument or None if not found
        """
        return self._repository.update(document)

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete PDF document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            True if marked as deleted, False if not found
        """
        return self._repository.soft_delete(doc_id)

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete PDF document by ID.

        Args:
            doc_id: Document unique identifier

        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete_by_id(doc_id)

    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted PDF document.

        Args:
            doc_id: Document unique identifier

        Returns:
            True if restored, False if not found
        """
        return self._repository.restore(doc_id)

    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process a new PDF and persist to MongoDB.

        Flujo completo:
        1. Valida el archivo
        2. Genera checksum para detectar duplicados
        3. Si existe, retorna el documento existente
        4. Si no, extrae texto y persiste en MongoDB

        Args:
            file_content: Binary PDF content
            filename: Original filename

        Returns:
            PDFDocument with extracted data (existing if duplicate, new if not)

        Raises:
            InvalidFileException: If file is not valid
            PDFExtractionException: If extraction fails
            DuplicateDocumentException: If checksum collision (con ID existente)
        """
        _validate_filename(filename)
        _validate_content(file_content)

        try:
            checksum = self.generate_checksum(file_content)
            existing = self.find_by_checksum(checksum)
            if existing:
                raise DuplicateDocumentException(
                    f"Document with checksum {checksum} already exists",
                    existing_id=existing.id,
                )

            text, page_count = pdf_extractor.extract_text(file_content)

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

    async def extract_text_from_pdf(
        self, doc_id: str, start_page: int = 1, end_page: int = 0
    ) -> PDFDocument:
        """Get text from existing persisted PDF.

        Como los documentos ya tienen el texto extraído almacenado
        en MongoDB, este método simplemente retorna el documento
        con su contenido completo. Los parámetros de página son
        ignorados ya que el texto ya está disponible.

        Args:
            doc_id: Unique identifier of the PDF
            start_page: Ignored (kept for API compatibility)
            end_page: Ignored (kept for API compatibility)

        Returns:
            PDFDocument with stored text content

        Raises:
            PDFNotFoundException: If document not found
        """
        doc = self._repository.find_by_id(doc_id)
        if doc is None:
            raise PDFNotFoundException(f"PDF not found: {doc_id}")
        return doc
