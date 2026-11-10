"""MongoDB adapter for the PDFRepository port."""

import logging
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.domain.pdf_document import PDFDocument
from app.domain.ports import PDFRepository
from app.exceptions import DuplicateDocumentException, RepositoryException

logger = logging.getLogger(__name__)

COLLECTION_NAME = "pdf_documents"


class MongoPDFRepository(PDFRepository):
    """Persist PDF documents in a MongoDB collection.

    Driver errors are translated into RepositoryException (HTTP 500) instead
    of being hidden as "not found", so an outage never looks like a 404.
    """

    def __init__(self, database: Database):
        self._collection: Collection = database[COLLECTION_NAME]

    def create(self, document: PDFDocument) -> PDFDocument:
        try:
            result = self._collection.insert_one(_to_mongo(document))
        except DuplicateKeyError as e:
            existing = self.find_by_checksum(document.checksum)
            raise DuplicateDocumentException(
                f"Document with checksum {document.checksum} already exists",
                existing_id=existing.id if existing else None,
            ) from e
        except PyMongoError as e:
            raise RepositoryException("Failed to create document") from e
        document.id = str(result.inserted_id)
        logger.info("Document created in MongoDB: %s", document.id)
        return document

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        object_id = _parse_object_id(doc_id)
        if object_id is None:
            return None
        return self._find_one({"_id": object_id})

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        return self._find_one({"checksum": checksum})

    def find_all(self) -> List[PDFDocument]:
        try:
            return [_from_mongo(doc) for doc in self._collection.find().sort("created_at", -1)]
        except PyMongoError as e:
            raise RepositoryException("Failed to list documents") from e

    def delete_by_id(self, doc_id: str) -> bool:
        object_id = _parse_object_id(doc_id)
        if object_id is None:
            return False
        try:
            return self._collection.delete_one({"_id": object_id}).deleted_count > 0
        except PyMongoError as e:
            raise RepositoryException("Failed to delete document") from e

    def _find_one(self, query: dict) -> Optional[PDFDocument]:
        try:
            doc = self._collection.find_one(query)
        except PyMongoError as e:
            raise RepositoryException("Failed to read document") from e
        return _from_mongo(doc) if doc else None


def _parse_object_id(doc_id: str) -> Optional[ObjectId]:
    """Return the ObjectId, or None when the id is malformed (treated as not found)."""
    try:
        return ObjectId(doc_id)
    except (InvalidId, TypeError):
        logger.debug("Invalid ObjectId: %s", doc_id)
        return None


def _to_mongo(document: PDFDocument) -> dict:
    return {
        "checksum": document.checksum,
        "filename": document.filename,
        "content_type": document.content_type,
        "text_content": document.text_content,
        "page_count": document.page_count,
        "file_size": document.file_size,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
    }


def _from_mongo(doc: dict) -> PDFDocument:
    return PDFDocument(
        id=str(doc["_id"]),
        checksum=doc["checksum"],
        filename=doc["filename"],
        content_type=doc.get("content_type", "application/pdf"),
        text_content=doc["text_content"],
        page_count=doc.get("page_count", 0),
        file_size=doc.get("file_size", 0),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )
