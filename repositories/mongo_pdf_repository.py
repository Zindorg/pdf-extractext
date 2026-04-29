"""MongoDB implementation of PDF repository."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from models.pdf_document import PDFDocument
from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


class MongoPDFRepository(PDFRepositoryInterface):
    """MongoDB implementation of PDF repository."""

    def __init__(self, mongo_client: MongoClient, database: str = "pdf_extractext"):
        """Initialize repository with MongoDB client.

        Args:
            mongo_client: Configured PyMongo client instance
            database: Database name to use
        """
        self._client: MongoClient = mongo_client
        self._db: Database = mongo_client[database]
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
            "deleted_at": pdf_doc.deleted_at,
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
            deleted_at=doc.get("deleted_at"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    def create(self, document: PDFDocument) -> PDFDocument:
        """Create a new PDF document in MongoDB."""
        doc_dict = self._to_document(document)
        if doc_dict["_id"] is None:
            del doc_dict["_id"]
        result = self._collection.insert_one(doc_dict)
        document.id = str(result.inserted_id)
        return document

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find active document by MongoDB ObjectId."""
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return None

        doc = self._collection.find_one({"_id": object_id, "deleted_at": None})
        if doc:
            return self._from_document(doc)
        return None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find active document by SHA-256 checksum."""
        doc = self._collection.find_one({"checksum": checksum, "deleted_at": None})
        if doc:
            return self._from_document(doc)
        return None

    def find_all(self) -> List[PDFDocument]:
        """Find all active documents."""
        documents = self._collection.find({"deleted_at": None})
        return [self._from_document(doc) for doc in documents]

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete document by ID."""
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return False

        result = self._collection.update_one(
            {"_id": object_id, "deleted_at": None},
            {
                "$set": {
                    "deleted_at": datetime.now(),
                    "updated_at": datetime.now(),
                }
            },
        )
        return result.modified_count > 0

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete document by ID."""
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return False

        result = self._collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    # Async methods from interface - not implemented for MongoDB
    async def save(self, file_content: bytes, filename: str) -> Path:
        """Not implemented - use create() instead."""
        raise NotImplementedError("Use create() for MongoDB persistence")

    async def get(self, file_id: str) -> Optional[Path]:
        """Not implemented - use find_by_id() instead."""
        raise NotImplementedError("Use find_by_id() for MongoDB retrieval")

    async def delete(self, file_id: str) -> bool:
        """Not implemented - use soft_delete() instead."""
        raise NotImplementedError("Use soft_delete() for MongoDB deletion")
