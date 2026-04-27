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
            "checksum": pdf_doc.checksum,
            "filename": pdf_doc.filename,
            "content_type": pdf_doc.content_type,
            "text_content": pdf_doc.text_content,
            "page_count": pdf_doc.page_count,
            "file_size": pdf_doc.file_size,
            "created_at": pdf_doc.created_at or datetime.now(),
            "updated_at": pdf_doc.updated_at or datetime.now()
        }

    def _from_document(self, doc: dict) -> PDFDocument:
        """Convert MongoDB document to PDFDocument."""
        return PDFDocument(
            id=str(doc["_id"]),
            checksum=doc["checksum"],
            filename=doc["filename"],
            content_type=doc.get("content_type", "application/pdf"),
            text_content=doc["text_content"],
            page_count=doc["page_count"],
            file_size=doc["file_size"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )

    def create(self, document: PDFDocument) -> PDFDocument:
        """Create a new PDF document in MongoDB."""
        doc_dict = self._to_document(document)
        result = self._collection.insert_one(doc_dict)
        document.id = str(result.inserted_id)
        return document

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find document by MongoDB ObjectId."""
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return None

        doc = self._collection.find_one({"_id": object_id})
        if doc:
            return self._from_document(doc)
        return None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find document by SHA-256 checksum."""
        doc = self._collection.find_one({"checksum": checksum})
        if doc:
            return self._from_document(doc)
        return None

    def find_all(self) -> List[PDFDocument]:
        """Find all documents."""
        documents = self._collection.find()
        return [self._from_document(doc) for doc in documents]

    def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID."""
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
        """Not implemented - use delete_by_id() instead."""
        raise NotImplementedError("Use delete_by_id() for MongoDB deletion")
