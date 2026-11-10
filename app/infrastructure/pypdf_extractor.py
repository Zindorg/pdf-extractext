"""pypdf adapter for the PDFTextExtractor port."""

import logging
from io import BytesIO

from pypdf import PdfReader

from app.domain.ports import ExtractedText, PDFTextExtractor
from app.domain.exceptions import PDFExtractionException

logger = logging.getLogger(__name__)


class PypdfTextExtractor(PDFTextExtractor):
    """Extract text from PDFs using pypdf."""

    def extract(self, file_content: bytes) -> ExtractedText:
        try:
            reader = PdfReader(BytesIO(file_content))
            pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as e:  # pypdf lanza tipos variados ante PDFs corruptos
            logger.warning("pypdf could not read the file: %s", e)
            raise PDFExtractionException(f"Invalid or corrupt PDF: {e}") from e
        text = "\n".join(pages).strip()
        logger.debug("Extracted %d pages, %d characters", len(pages), len(text))
        return ExtractedText(text=text, page_count=len(pages))
