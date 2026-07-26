"""PDF text extraction functions using pypdf."""

import logging
from io import BytesIO
from typing import Tuple

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text(file_content: bytes) -> Tuple[str, int]:
    """Extract text from PDF.

    Returns:
        Tuple of (extracted_text, page_count)
    """
    logger.debug("Starting PDF text extraction (%d bytes)", len(file_content))
    reader = PdfReader(BytesIO(file_content))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    page_count = len(reader.pages)
    full_text = "\n".join(text_parts).strip()
    logger.debug("Extracted %d pages, %d characters", page_count, len(full_text))
    return full_text, page_count

