"""PDF text extraction functions using pypdf."""

import logging
from io import BytesIO
from typing import Tuple

from pypdf import PdfReader

from app.exceptions import PDFExtractionException

logger = logging.getLogger(__name__)


def extract_text(file_content: bytes) -> Tuple[str, int]:
    """Extract text from PDF.

    Returns:
        Tuple of (extracted_text, page_count)

    Raises:
        PDFExtractionException: If the content cannot be parsed as a PDF.
    """
    logger.debug("Starting PDF text extraction (%d bytes)", len(file_content))
    try:
        reader = PdfReader(BytesIO(file_content))
        text_parts = [page.extract_text() or "" for page in reader.pages]
    except Exception as e:  # pypdf lanza tipos variados ante PDFs corruptos
        logger.warning("pypdf could not read the file: %s", e)
        raise PDFExtractionException(f"Invalid or corrupt PDF: {e}") from e
    page_count = len(text_parts)
    full_text = "\n".join(text_parts).strip()
    logger.debug("Extracted %d pages, %d characters", page_count, len(full_text))
    return full_text, page_count