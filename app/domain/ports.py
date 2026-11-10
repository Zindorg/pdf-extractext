"""Ports: abstractions the domain needs from the outside world.

The use cases depend on these interfaces; the infrastructure layer
provides the adapters (MongoDB, pypdf) and the composition root
(`app/dependencies.py`) wires them together.
"""

from abc import ABC, abstractmethod
from typing import List, NamedTuple, Optional

from app.domain.pdf_document import PDFDocument


class ExtractedText(NamedTuple):
    """Result of reading a PDF."""

    text: str
    page_count: int


class PDFTextExtractor(ABC):
    """Reads the text out of a PDF file."""

    @abstractmethod
    def extract(self, file_content: bytes) -> ExtractedText:
        """Extract the text of every page.

        Raises:
            PDFExtractionException: If the content is not a readable PDF.
        """


class PDFReader(ABC):
    """Read access to stored PDF documents."""

    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find a document by id; None if it does not exist or the id is invalid."""

    @abstractmethod
    def find_all(self) -> List[PDFDocument]:
        """Return all documents, newest first."""


class PDFWriter(ABC):
    """Write access to stored PDF documents."""

    @abstractmethod
    def create(self, document: PDFDocument) -> PDFDocument:
        """Persist a new document and return it with its id.

        Raises:
            DuplicateDocumentException: If a document with the same checksum exists.
        """

    @abstractmethod
    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete a document; True if something was deleted."""
