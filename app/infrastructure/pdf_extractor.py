"""PDF text extraction functions using pypdf."""

from io import BytesIO
from typing import Tuple

from pypdf import PdfReader


def extract_text(file_content: bytes) -> Tuple[str, int]:
    """Extract text from PDF.

    Returns:
        Tuple of (extracted_text, page_count)
    """
    reader = PdfReader(BytesIO(file_content))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    page_count = len(reader.pages)
    return "\n".join(text_parts).strip(), page_count

