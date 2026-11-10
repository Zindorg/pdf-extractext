"""Use case: list all persisted PDFs."""

from typing import List

from app.domain.pdf_document import PDFDocument
from app.domain.ports import PDFRepository


class ListPDFs:
    """Return every persisted document, newest first."""

    def __init__(self, repository: PDFRepository) -> None:
        self._repository = repository

    def execute(self) -> List[PDFDocument]:
        return self._repository.find_all()
