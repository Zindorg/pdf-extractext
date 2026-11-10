"""Fakes en memoria que respetan los contratos de los puertos de la app.

A diferencia de un MagicMock, un fake tiene comportamiento real: guarda,
busca y borra. Así los tests verifican conducta observable y no la
existencia de llamadas internas. El test de contrato del repositorio
(tests/contract) garantiza que este fake se comporta igual que MongoDB.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional

from bson import ObjectId

from app.domain.pdf_document import PDFDocument
from app.domain.ports import ExtractedText, PDFRepository, PDFTextExtractor
from app.domain.exceptions import DuplicateDocumentException, PDFExtractionException


class InMemoryPDFRepository(PDFRepository):
    """Repositorio en memoria con las mismas reglas que el de MongoDB."""

    def __init__(self) -> None:
        self._docs: Dict[str, PDFDocument] = {}

    def create(self, document: PDFDocument) -> PDFDocument:
        if self.find_by_checksum(document.checksum):
            raise DuplicateDocumentException(
                f"Document with checksum {document.checksum} already exists"
            )
        document.id = str(ObjectId())
        self._docs[document.id] = copy.deepcopy(document)
        return document

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        doc = self._docs.get(doc_id)
        return copy.deepcopy(doc) if doc else None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        match = next((d for d in self._docs.values() if d.checksum == checksum), None)
        return copy.deepcopy(match) if match else None

    def find_all(self) -> List[PDFDocument]:
        docs = sorted(self._docs.values(), key=lambda d: d.created_at, reverse=True)
        return [copy.deepcopy(d) for d in docs]

    def delete_by_id(self, doc_id: str) -> bool:
        return self._docs.pop(doc_id, None) is not None


class FakeTextExtractor(PDFTextExtractor):
    """Extractor que interpreta los bytes como texto UTF-8 de una página.

    `b"CORRUPT"` simula un archivo ilegible.
    """

    def extract(self, file_content: bytes) -> ExtractedText:
        if file_content == b"CORRUPT":
            raise PDFExtractionException("Invalid or corrupt PDF")
        return ExtractedText(text=file_content.decode().strip(), page_count=1)
