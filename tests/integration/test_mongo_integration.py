"""Integration tests for MongoDB CRUD operations.

Estos tests requieren una instancia de MongoDB corriendo.
Se pueden ejecutar con: pytest tests/integration/ -v --integration
"""

import os
import pytest
from datetime import datetime
from bson import ObjectId

# Skip all tests if SKIP_INTEGRATION_TESTS is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)

# Import after skip check
from models.pdf_document import PDFDocument
from repositories.mongo_pdf_repository import MongoPDFRepository
from core.exceptions import DuplicateDocumentException, RepositoryException


@pytest.fixture(scope="module")
def mongo_repository():
    """Provide MongoDB repository connected to test database.
    
    Nota: Requiere MongoDB corriendo en localhost:27017
    """
    from infrastructure.database_connection import get_database
    
    try:
        db = get_database()
        repository = MongoPDFRepository(database=db)
        
        # Clean up any existing test data
        db["pdf_documents"].delete_many({"filename": {"$regex": "^test_"}})
        
        yield repository
        
        # Cleanup after tests
        db["pdf_documents"].delete_many({"filename": {"$regex": "^test_"}})
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")


class TestCreateDocument:
    """Test CREATE operation."""

    def test_create_persists_document_to_database(self, mongo_repository):
        """Verify document is actually saved to MongoDB."""
        document = PDFDocument(
            checksum="test_create_123",
            filename="test_create.pdf",
            text_content="Integration test content",
            page_count=5,
            file_size=1024,
        )

        result = mongo_repository.create(document)

        assert result.id is not None
        assert isinstance(result.id, str)
        
        # Verify in database directly
        raw_doc = mongo_repository._collection.find_one(
            {"_id": ObjectId(result.id)}
        )
        assert raw_doc is not None
        assert raw_doc["checksum"] == "test_create_123"
        assert raw_doc["text_content"] == "Integration test content"

    def test_create_generates_timestamps(self, mongo_repository):
        """Verify created_at and updated_at are set automatically."""
        document = PDFDocument(
            checksum="test_timestamps_456",
            filename="test_timestamps.pdf",
            text_content="Test content",
        )

        result = mongo_repository.create(document)

        raw_doc = mongo_repository._collection.find_one(
            {"_id": ObjectId(result.id)}
        )
        assert raw_doc["created_at"] is not None
        assert raw_doc["updated_at"] is not None
        assert isinstance(raw_doc["created_at"], datetime)

    def test_create_raises_duplicate_exception_on_checksum_collision(self, mongo_repository):
        """Verify unique constraint on checksum works."""
        checksum = "test_duplicate_collision"
        
        # Create first document
        doc1 = PDFDocument(
            checksum=checksum,
            filename="test_first.pdf",
            text_content="First document",
        )
        mongo_repository.create(doc1)

        # Try to create duplicate
        doc2 = PDFDocument(
            checksum=checksum,
            filename="test_second.pdf",
            text_content="Second document",
        )

        with pytest.raises(DuplicateDocumentException) as exc_info:
            mongo_repository.create(doc2)

        assert exc_info.value.existing_id is not None
        assert "already exists" in str(exc_info.value)


class TestFindByChecksum:
    """Test READ by checksum operation."""

    def test_find_by_checksum_returns_document(self, mongo_repository):
        """Verify finding by checksum returns correct document."""
        checksum = "test_find_checksum"
        document = PDFDocument(
            checksum=checksum,
            filename="test_find.pdf",
            text_content="Find me",
            page_count=10,
        )
        created = mongo_repository.create(document)

        result = mongo_repository.find_by_checksum(checksum)

        assert result is not None
        assert result.id == created.id
        assert result.checksum == checksum
        assert result.page_count == 10

    def test_find_by_checksum_returns_none_for_nonexistent(self, mongo_repository):
        """Verify finding non-existent checksum returns None."""
        result = mongo_repository.find_by_checksum("nonexistent_checksum_xyz")
        assert result is None


class TestFindById:
    """Test READ by ID operation."""

    def test_find_by_id_returns_document(self, mongo_repository):
        """Verify finding by ID returns correct document."""
        document = PDFDocument(
            checksum="test_find_id",
            filename="test_find_id.pdf",
            text_content="Find by ID test",
        )
        created = mongo_repository.create(document)

        result = mongo_repository.find_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.text_content == "Find by ID test"

    def test_find_by_id_returns_none_for_invalid_format(self, mongo_repository):
        """Verify invalid ID format returns None."""
        result = mongo_repository.find_by_id("invalid-id-format")
        assert result is None

    def test_find_by_id_returns_none_for_nonexistent(self, mongo_repository):
        """Verify non-existent ID returns None."""
        fake_id = "507f1f77bcf86cd799439099"
        result = mongo_repository.find_by_id(fake_id)
        assert result is None


class TestFindAll:
    """Test READ all operation."""

    def test_find_all_returns_list_of_documents(self, mongo_repository):
        """Verify find_all returns all non-deleted documents."""
        # Create multiple documents
        for i in range(3):
            doc = PDFDocument(
                checksum=f"test_list_{i}",
                filename=f"test_list_{i}.pdf",
                text_content=f"Content {i}",
            )
            mongo_repository.create(doc)

        results = mongo_repository.find_all()

        assert len(results) >= 3
        checksums = [doc.checksum for doc in results]
        assert "test_list_0" in checksums
        assert "test_list_1" in checksums
        assert "test_list_2" in checksums

    def test_find_all_excludes_deleted_documents(self, mongo_repository):
        """Verify deleted documents are excluded from results."""
        # Create and then delete a document
        doc = PDFDocument(
            checksum="test_exclude_deleted",
            filename="test_exclude.pdf",
            text_content="To be deleted",
        )
        created = mongo_repository.create(doc)
        mongo_repository.soft_delete(created.id)

        results = mongo_repository.find_all()

        checksums = [d.checksum for d in results]
        assert "test_exclude_deleted" not in checksums


class TestUpdateDocument:
    """Test UPDATE operation."""

    def test_update_modifies_document_fields(self, mongo_repository):
        """Verify update changes document fields."""
        # Create initial document
        doc = PDFDocument(
            checksum="test_update",
            filename="test_update.pdf",
            text_content="Original content",
            page_count=5,
        )
        created = mongo_repository.create(doc)

        # Update document
        created.text_content = "Updated content"
        created.page_count = 10
        updated = mongo_repository.update(created)

        assert updated is not None
        assert updated.text_content == "Updated content"
        assert updated.page_count == 10

        # Verify in database
        result = mongo_repository.find_by_id(created.id)
        assert result.text_content == "Updated content"

    def test_update_returns_none_for_nonexistent(self, mongo_repository):
        """Verify updating non-existent document returns None."""
        doc = PDFDocument(
            id="507f1f77bcf86cd799439099",
            checksum="nonexistent",
            filename="fake.pdf",
            text_content="content",
        )

        result = mongo_repository.update(doc)
        assert result is None


class TestSoftDelete:
    """Test SOFT DELETE operation."""

    def test_soft_delete_marks_document_as_deleted(self, mongo_repository):
        """Verify soft delete sets deleted_at timestamp."""
        doc = PDFDocument(
            checksum="test_soft_delete",
            filename="test_soft_delete.pdf",
            text_content="To be soft deleted",
        )
        created = mongo_repository.create(doc)

        result = mongo_repository.soft_delete(created.id)

        assert result is True

        # Document should not appear in find_all
        all_docs = mongo_repository.find_all()
        ids = [d.id for d in all_docs]
        assert created.id not in ids

        # But should exist in database with deleted_at
        raw_doc = mongo_repository._collection.find_one(
            {"_id": ObjectId(created.id)}
        )
        assert raw_doc["deleted_at"] is not None

    def test_soft_delete_returns_false_for_nonexistent(self, mongo_repository):
        """Verify soft deleting non-existent document returns False."""
        result = mongo_repository.soft_delete("507f1f77bcf86cd799439099")
        assert result is False


class TestDeleteById:
    """Test HARD DELETE operation."""

    def test_delete_permanently_removes_document(self, mongo_repository):
        """Verify hard delete removes document completely."""
        doc = PDFDocument(
            checksum="test_hard_delete",
            filename="test_hard_delete.pdf",
            text_content="To be permanently deleted",
        )
        created = mongo_repository.create(doc)

        result = mongo_repository.delete_by_id(created.id)

        assert result is True

        # Document should not exist at all
        raw_doc = mongo_repository._collection.find_one(
            {"_id": ObjectId(created.id)}
        )
        assert raw_doc is None

    def test_delete_returns_false_for_nonexistent(self, mongo_repository):
        """Verify deleting non-existent document returns False."""
        result = mongo_repository.delete_by_id("507f1f77bcf86cd799439099")
        assert result is False


class TestRestore:
    """Test RESTORE operation."""

    def test_restore_recovers_soft_deleted_document(self, mongo_repository):
        """Verify restore recovers soft-deleted document."""
        doc = PDFDocument(
            checksum="test_restore",
            filename="test_restore.pdf",
            text_content="To be restored",
        )
        created = mongo_repository.create(doc)
        mongo_repository.soft_delete(created.id)

        # Verify deleted
        assert mongo_repository.find_by_id(created.id) is None

        # Restore
        result = mongo_repository.restore(created.id)
        assert result is True

        # Should be findable again
        restored = mongo_repository.find_by_id(created.id)
        assert restored is not None
        assert restored.checksum == "test_restore"

    def test_restore_returns_false_for_non_deleted_document(self, mongo_repository):
        """Verify restoring non-deleted document returns False."""
        doc = PDFDocument(
            checksum="test_restore_active",
            filename="test_restore_active.pdf",
            text_content="Active document",
        )
        created = mongo_repository.create(doc)

        result = mongo_repository.restore(created.id)
        assert result is False


class TestDocumentLifecycle:
    """Test complete CRUD lifecycle."""

    def test_full_create_read_update_delete_cycle(self, mongo_repository):
        """Verify complete document lifecycle."""
        # CREATE
        doc = PDFDocument(
            checksum="test_lifecycle",
            filename="test_lifecycle.pdf",
            text_content="Initial content",
            page_count=5,
        )
        created = mongo_repository.create(doc)
        assert created.id is not None

        # READ
        found = mongo_repository.find_by_id(created.id)
        assert found.text_content == "Initial content"

        # UPDATE
        found.text_content = "Updated content"
        updated = mongo_repository.update(found)
        assert updated.text_content == "Updated content"

        # SOFT DELETE
        assert mongo_repository.soft_delete(created.id) is True
        assert mongo_repository.find_by_id(created.id) is None

        # RESTORE
        assert mongo_repository.restore(created.id) is True
        restored = mongo_repository.find_by_id(created.id)
        assert restored is not None

        # HARD DELETE
        assert mongo_repository.delete_by_id(created.id) is True
        assert mongo_repository.find_by_id(created.id) is None
