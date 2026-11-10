"""Fakes en memoria que respetan los contratos de los puertos de la app.

A diferencia de un MagicMock, un fake tiene comportamiento real: guarda,
busca y borra. Así los tests verifican conducta observable y no la
existencia de llamadas internas.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional

from bson import ObjectId

from app.exceptions import DuplicateDocumentException
from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


class InMemoryPDFRepository(PDFRepositoryInterface):
    """Repositorio en memoria con las mismas reglas que el de MongoDB."""

    def __init__(self) -> None:
        self._docs: Dict[str, PDFDocument] = {}

    def create(self, document: PDFDocument) -> PDFDocument:
        if any(d.checksum == document.checksum for d in self._docs.values()):
            raise DuplicateDocumentException(
                f"Document with checksum {document.checksum} already exists"
            )
        document.id = document.id or str(ObjectId())
        self._docs[document.id] = copy.deepcopy(document)
        return document

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        doc = self._docs.get(doc_id)
        return copy.deepcopy(doc) if doc else None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        for doc in self._docs.values():
            if doc.checksum == checksum:
                return copy.deepcopy(doc)
        return None

    def find_all(self) -> List[PDFDocument]:
        docs = sorted(self._docs.values(), key=lambda d: d.created_at, reverse=True)
        return [copy.deepcopy(d) for d in docs]

    def delete_by_id(self, doc_id: str) -> bool:
        return self._docs.pop(doc_id, None) is not None

    # --- Métodos heredados de la interfaz actual (se eliminan en la Fase 2) ---
    def update(self, document):  # pragma: no cover
        raise NotImplementedError

    def soft_delete(self, doc_id):  # pragma: no cover
        raise NotImplementedError

    def restore(self, doc_id):  # pragma: no cover
        raise NotImplementedError
