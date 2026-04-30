"""MongoDB implementation of PDF repository with robust CRUD operations."""

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.exceptions import DuplicateDocumentException, RepositoryException
from app.infrastructure.database_connection import get_database
from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


class MongoPDFRepository(PDFRepositoryInterface):
    """MongoDB implementation of PDF repository.

    Implementa todas las operaciones CRUD para documentos PDF,
    con manejo robusto de errores y validación de duplicados.

    Attributes:
        _db: Instancia de base de datos MongoDB.
        _collection: Colección de documentos PDF.

    Example:
        >>> from repositories.mongo_pdf_repository import MongoPDFRepository
        >>> from infrastructure.database_connection import get_database
        >>> repo = MongoPDFRepository(database=get_database())
        >>> doc = repo.find_by_checksum("abc123")
    """

    def __init__(self, database: Database = None):
        """Initialize repository with database connection.

        Args:
            database: MongoDB database instance. If None, uses singleton.
        """
        self._db: Database = database or get_database()
        self._collection: Collection = self._db["pdf_documents"]

    def _to_document(self, pdf_doc: PDFDocument) -> dict:
        """Convert PDFDocument to MongoDB document.

        Args:
            pdf_doc: Domain model to convert.

        Returns:
            Dictionary representation for MongoDB.
        """
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
        """Convert MongoDB document to PDFDocument.

        Args:
            doc: MongoDB document dictionary.

        Returns:
            Domain model instance.
        """
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
        """Create a new PDF document in MongoDB.

        Persiste un nuevo documento PDF en la base de datos.
        Si el documento ya existe (mismo checksum), lanza excepción.

        Args:
            document: PDFDocument to persist.

        Returns:
            PDFDocument with assigned ID.

        Raises:
            DuplicateDocumentException: If checksum already exists.
            RepositoryException: If database operation fails.

        Example:
            >>> doc = PDFDocument(
            ...     checksum="abc123",
            ...     filename="test.pdf",
            ...     text_content="content"
            ... )
            >>> saved = repo.create(doc)
            >>> print(saved.id)  # MongoDB ObjectId as string
        """
        doc_dict = self._to_document(document)
        if doc_dict["_id"] is None:
            del doc_dict["_id"]

        try:
            result = self._collection.insert_one(doc_dict)
            document.id = str(result.inserted_id)
            return document
        except DuplicateKeyError as e:
            existing = self.find_by_checksum(document.checksum)
            raise DuplicateDocumentException(
                f"Document with checksum {document.checksum} already exists",
                existing_id=existing.id if existing else None,
            ) from e
        except PyMongoError as e:
            raise RepositoryException(f"Failed to create document: {e}") from e

    def find_by_id(self, doc_id: str) -> Optional[PDFDocument]:
        """Find active document by MongoDB ObjectId.

        Busca un documento por su ID, excluyendo los marcados
        como eliminados (soft delete).

        Args:
            doc_id: Document unique identifier (MongoDB ObjectId string).

        Returns:
            PDFDocument or None if not found or deleted.

        Example:
            >>> doc = repo.find_by_id("507f1f77bcf86cd799439011")
            >>> if doc:
            ...     print(doc.filename)
        """
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return None

        try:
            doc = self._collection.find_one({"_id": object_id, "deleted_at": None})
            if doc:
                return self._from_document(doc)
            return None
        except PyMongoError:
            return None

    def find_by_checksum(self, checksum: str) -> Optional[PDFDocument]:
        """Find active document by SHA-256 checksum.

        Busca un documento por su hash de contenido, útil para
        detectar duplicados.

        Args:
            checksum: SHA-256 checksum string.

        Returns:
            PDFDocument or None if not found or deleted.

        Example:
            >>> existing = repo.find_by_checksum("abc123...")
            >>> if existing:
            ...     print("Duplicate detected!")
        """
        try:
            doc = self._collection.find_one({"checksum": checksum, "deleted_at": None})
            if doc:
                return self._from_document(doc)
            return None
        except PyMongoError:
            return None

    def find_all(self) -> List[PDFDocument]:
        """Find all active documents.

        Retorna todos los documentos no eliminados, ordenados
        por fecha de creación descendente.

        Returns:
            List of active PDFDocuments.

        Example:
            >>> documents = repo.find_all()
            >>> for doc in documents:
            ...     print(f"{doc.filename}: {doc.page_count} pages")
        """
        try:
            documents = self._collection.find({"deleted_at": None}).sort(
                "created_at", -1
            )
            return [self._from_document(doc) for doc in documents]
        except PyMongoError:
            return []

    def update(self, document: PDFDocument) -> Optional[PDFDocument]:
        """Update an existing PDF document.

        Actualiza un documento existente. Solo se actualizan
        los campos permitidos (no se puede cambiar checksum).

        Args:
            document: PDFDocument with updated fields.

        Returns:
            Updated PDFDocument or None if not found.

        Raises:
            RepositoryException: If update fails.

        Example:
            >>> doc = repo.find_by_id("507f1f77bcf86cd799439011")
            >>> doc.update_text("new content")
            >>> updated = repo.update(doc)
        """
        if not document.id:
            return None

        try:
            object_id = ObjectId(document.id)
        except Exception:
            return None

        update_data = {
            "$set": {
                "text_content": document.text_content,
                "page_count": document.page_count,
                "file_size": document.file_size,
                "updated_at": datetime.now(),
            }
        }

        try:
            result = self._collection.update_one(
                {"_id": object_id, "deleted_at": None},
                update_data,
            )
            if result.modified_count > 0:
                return self.find_by_id(document.id)
            return None
        except PyMongoError as e:
            raise RepositoryException(f"Failed to update document: {e}") from e

    def soft_delete(self, doc_id: str) -> bool:
        """Soft delete document by ID.

        Marca un documento como eliminado estableciendo
        el timestamp deleted_at, sin borrarlo físicamente.

        Args:
            doc_id: Document unique identifier.

        Returns:
            True if marked as deleted, False if not found.

        Example:
            >>> if repo.soft_delete("507f1f77bcf86cd799439011"):
            ...     print("Document archived")
        """
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return False

        try:
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
        except PyMongoError:
            return False

    def delete_by_id(self, doc_id: str) -> bool:
        """Permanently delete document by ID.

        Elimina físicamente un documento de la base de datos.
        Use con precaución - preferir soft_delete.

        Args:
            doc_id: Document unique identifier.

        Returns:
            True if deleted, False if not found.

        Example:
            >>> if repo.delete_by_id("507f1f77bcf86cd799439011"):
            ...     print("Permanently deleted")
        """
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return False

        try:
            result = self._collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except PyMongoError:
            return False

    def restore(self, doc_id: str) -> bool:
        """Restore a soft-deleted document.

        Recupera un documento previamente marcado como eliminado,
        limpiando el campo deleted_at.

        Args:
            doc_id: Document unique identifier.

        Returns:
            True if restored, False if not found.

        Example:
            >>> if repo.restore("507f1f77bcf86cd799439011"):
            ...     print("Document recovered")
        """
        try:
            object_id = ObjectId(doc_id)
        except Exception:
            return False

        try:
            result = self._collection.update_one(
                {"_id": object_id, "deleted_at": {"$ne": None}},
                {
                    "$set": {"updated_at": datetime.now()},
                    "$unset": {"deleted_at": ""},
                },
            )
            return result.modified_count > 0
        except PyMongoError:
            return False
