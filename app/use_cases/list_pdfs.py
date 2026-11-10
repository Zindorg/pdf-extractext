"""Use case: list all persisted PDFs."""

from typing import List

from app.domain.pdf_document import PDFDocument
from app.domain.ports import PDFReader


class ListPDFs:
    """Return every persisted document, newest first."""

    def __init__(self, reader: PDFReader) -> None:
        self._reader = reader

    def execute(self) -> List[PDFDocument]:
        return self._reader.find_all()
