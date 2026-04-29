"""Domain entity for PDF documents."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PDFDocument:
    """Entity representing a PDF document."""

    checksum: str
    filename: str
    text_content: str
    id: Optional[str] = None
    content_type: str = "application/pdf"
    page_count: int = 0
    file_size: int = 0
    deleted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_text(self, text: str) -> None:
        """Update text content and timestamp."""
        self.text_content = text
        self.updated_at = datetime.now()
