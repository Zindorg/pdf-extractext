"""Domain entity for PDF documents."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.exceptions import PDFExtractionException
from app.domain.uploaded_file import UploadedFile


@dataclass
class PDFDocument:
    """A PDF whose text has been extracted and can be stored."""

    checksum: str
    filename: str
    text_content: str
    id: Optional[str] = None
    page_count: int = 0
    file_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_upload(cls, file: UploadedFile, text: str, page_count: int) -> "PDFDocument":
        """Build a document from an upload; a PDF without text is rejected."""
        if not text.strip():
            raise PDFExtractionException("No text content extracted from PDF")
        return cls(
            checksum=file.checksum,
            filename=file.filename,
            text_content=text,
            page_count=page_count,
            file_size=file.size,
        )
