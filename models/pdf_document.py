"""Domain entity for PDF documents."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PDFDocument:
    """Entity representing a PDF document."""

    id: Optional[str] = None
    filename: str = ""
    content_type: str = "application/pdf"
    text_content: str = ""
    page_count: int = 0
    file_size: int = 0
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
