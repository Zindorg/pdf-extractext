"""PDF text extraction functions using pypdf."""

from io import BytesIO
from typing import Tuple

from pypdf import PdfReader


def extract_text(file_content: bytes) -> Tuple[str, int]:
    """Extract text from PDF. """
    reader = PdfReader(BytesIO(file_content))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    combined = "\n".join(text_parts).strip()

    if not combined:
        return "", 0

    return combined, len(reader.pages)



def extract_text_from_page_range(
    file_content: bytes, start_page: int, end_page: int
) -> Tuple[str, int]:
    """Extract text from a page range."""
    reader = PdfReader(BytesIO(file_content))
    total_pages = len(reader.pages)

    # Adjust to 0-based indexing
    start_idx = max(0, start_page - 1)
    end_idx = min(total_pages, end_page) if end_page > 0 else total_pages

    text_parts = [reader.pages[i].extract_text() or "" for i in range(start_idx, end_idx)]
    return "\n".join(text_parts), end_idx - start_idx
