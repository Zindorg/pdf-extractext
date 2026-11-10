"""MongoDB implementation of PDF repository with robust CRUD operations."""

import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.exceptions import DuplicateDocumentException, RepositoryException
from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface

logger = logging.getLogger(__name__)


class MongoPDFRepository(PDFRepositoryInterface):
    """MongoDB implementation of PDF repository."""

    def __init__(self, database: Database):
        """Initialize repository with database connection."""
        self._db: Database = database
        self._collection: Collection = self._db["pdf_documents"]

    def _to_document(self, pdf_doc: PDFDocument) -> dict:
        """Convert PDFDocument to MongoDB document."""
        return {
            "_id": ObjectId(pdf_doc.id) if pdf_doc.id else None,
            "checksum": pdf_doc.checksum,
            "filename": pdf_doc.filename,
            "content_type": pdf_doc.content_type,
            "text_content": pdf_doc.text_content,
            "page_count": pdf_doc.page_count,
            "file_size": pdf_doc.file_size,
            "created_at": pdf_doc.created_at or datetime.now(),
            "updated_at": pdf_doc.updated_at or datetime.now(),
        }

    def _from_document(self, doc: dict) -> PDFDocument:
        """Convert MongoDB document to PDFDocument."""
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

    def create(self, document: PDFDocument) -> PDFDocument:
        """Create a new PDF document in MongoDB."""
        doc_dict = self._to_document(document)
        if doc_dict["_id"] is None:
            del doc_dict["_id"]

        try:
            result = self._collection.insert_one(doc_dict)
            document.id = str(result.inserted_id)
            logger.info("Document created in MongoDB: %s", document.id)
            return document
        except DuplicateKeyError as e:
            existing = self.find_by_checksum(document.checksum)
            logger.warning("Duplicate key error for checksum: %s", document.checksum)
            raise DuplicateDocumentException(
                f"Document with checksum {document.checksum} already exists",
                existing_id=existing.id if existing else None,
            ) from e
        except PyMongoError as e:
            logger.error("Failed to create document in MongoDB: %s", e)
            raise RepositoryException(f"Failed to create document: {e}") from e

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find document by MongoDB ObjectId."""
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            logger.warning("Invalid ObjectId format: %s", doc_id)
            return None

        try:
            doc = self._collection.find_one({"_id": object_id})
            if doc:
                logger.debug("Document found by id: %s", doc_id)
                return self._from_document(doc)
            logger.debug("Document not found by id: %s", doc_id)
            return None
        except PyMongoError:
            logger.error("MongoDB error while finding by id: %s", doc_id)
            return None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find document by SHA-256 checksum."""
        try:
            doc = self._collection.find_one({"checksum": checksum})
            if doc:
                logger.debug("Document found by checksum: %s", checksum)
                return self._from_document(doc)
            logger.debug("No document found for checksum: %s", checksum)
            return None
        except PyMongoError:
            logger.error("MongoDB error while finding by checksum: %s", checksum)
            return None

    def find_all(self) -> List[PDFDocument]:
        """Find all documents, newest first."""
        try:
            documents = self._collection.find().sort(
                "created_at", -1
            )
            docs = [self._from_document(doc) for doc in documents]
            logger.debug("Found %d documents", len(docs))
            return docs
        except PyMongoError:
            logger.error("MongoDB error while finding all documents")
            return []

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete document by ID."""
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            logger.warning("Hard delete failed: invalid ObjectId: %s", doc_id)
            return False

        try:
            result = self._collection.delete_one({"_id": object_id})
            if result.deleted_count > 0:
                logger.info("Document permanently deleted: %s", doc_id)
                return True
            logger.warning("Hard delete failed: document not found: %s", doc_id)
            return False
        except PyMongoError:
            logger.error("MongoDB error during hard delete: %s", doc_id)
            return False
