"""Tests for MongoPDFRepository - CRUD operations with proper error handling."""

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from bson import ObjectId

from models.pdf_document import PDFDocument
from repositories.mongo_pdf_repository import MongoPDFRepository


@pytest.fixture
def mock_database():
    """Create a mock MongoDB database."""
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__ = Mock(return_value=collection)
    db.pdf_documents = collection
    return db, collection


class TestCreateDocument:
    """Test Create operation."""

    def test_saves_document_with_metadata_and_text(self, mock_database):
        """Saves PDF document and returns with MongoDB generated ID."""
        db, collection = mock_database

        inserted_id = ObjectId("507f1f77bcf86cd799439011")
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        repository = MongoPDFRepository(database=db)
        document = PDFDocument(
            checksum="abc123checksum",
            filename="test.pdf",
            text_content="extracted text content",
            page_count=5,
            file_size=1024,
        )

        result = repository.create(document)

        assert result.id == str(inserted_id)
        assert result.checksum == "abc123checksum"
        assert result.text_content == "extracted text content"
        collection.insert_one.assert_called_once()

    def test_raises_duplicate_exception_on_checksum_collision(self, mock_database):
        """Raises DuplicateDocumentException when checksum already exists."""
        from pymongo.errors import DuplicateKeyError
        from core.exceptions import DuplicateDocumentException

        db, collection = mock_database
        collection.insert_one.side_effect = DuplicateKeyError("duplicate key")

        # Simulate existing document with same checksum
        existing_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "checksum": "duplicate_checksum",
            "filename": "existing.pdf",
            "text_content": "existing content",
            "deleted_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        collection.find_one.return_value = existing_doc

        repository = MongoPDFRepository(database=db)
        document = PDFDocument(
            checksum="duplicate_checksum",
            filename="test.pdf",
            text_content="new content",
        )

        with pytest.raises(DuplicateDocumentException) as exc_info:
            repository.create(document)

        assert exc_info.value.existing_id == "507f1f77bcf86cd799439011"


class TestFindByChecksum:
    """Test Read operation by checksum."""

    def test_finds_document_by_checksum(self, mock_database):
        """Finds existing document by its unique checksum."""
        db, collection = mock_database

        collection.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "checksum": "abc123",
            "filename": "test.pdf",
            "text_content": "content",
            "page_count": 1,
            "file_size": 100,
            "deleted_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_checksum("abc123")

        assert result is not None
        assert result.checksum == "abc123"
        collection.find_one.assert_called_with(
            {"checksum": "abc123", "deleted_at": None}
        )

    def test_returns_none_for_nonexistent_checksum(self, mock_database):
        """Returns None when checksum not found."""
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_checksum("nonexistent")

        assert result is None


class TestFindById:
    """Test Read operation by ID."""

    def test_gets_document_by_id(self, mock_database):
        """Returns document when searching by valid ID."""
        db, collection = mock_database

        object_id = ObjectId("507f1f77bcf86cd799439011")
        collection.find_one.return_value = {
            "_id": object_id,
            "checksum": "abc123",
            "filename": "test.pdf",
            "text_content": "content",
            "page_count": 1,
            "file_size": 100,
            "deleted_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_id("507f1f77bcf86cd799439011")

        assert result is not None
        assert result.id == "507f1f77bcf86cd799439011"
        assert result.filename == "test.pdf"

    def test_returns_none_for_invalid_id_format(self, mock_database):
        """Returns None for invalid MongoDB ID format."""
        db, _ = mock_database

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_id("invalid-non-mongo-id")

        assert result is None

    def test_returns_none_for_deleted_document(self, mock_database):
        """Returns None when document is soft-deleted."""
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_id("507f1f77bcf86cd799439011")

        assert result is None


class TestFindAll:
    """Test Read all operation."""

    def test_returns_list_of_active_documents(self, mock_database):
        """Returns list of non-deleted documents."""
        db, collection = mock_database

        collection.find.return_value.sort.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "checksum": "abc123",
                "filename": "doc1.pdf",
                "text_content": "content1",
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439012"),
                "checksum": "def456",
                "filename": "doc2.pdf",
                "text_content": "content2",
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        repository = MongoPDFRepository(database=db)
        results = repository.find_all()

        assert len(results) == 2
        assert results[0].filename == "doc1.pdf"
        assert results[1].filename == "doc2.pdf"
        collection.find.assert_called_with({"deleted_at": None})

    def test_returns_empty_list_when_no_documents(self, mock_database):
        """Returns empty list when no documents exist."""
        db, collection = mock_database
        collection.find.return_value.sort.return_value = []

        repository = MongoPDFRepository(database=db)
        results = repository.find_all()

        assert results == []


class TestUpdateDocument:
    """Test Update operation."""

    def test_updates_document_fields(self, mock_database):
        """Updates document and returns updated instance."""
        db, collection = mock_database

        # First update_one succeeds
        collection.update_one.return_value = Mock(modified_count=1)
        # Then find_one returns updated document
        collection.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "checksum": "abc123",
            "filename": "test.pdf",
            "text_content": "updated content",
            "page_count": 10,
            "file_size": 2048,
            "deleted_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        repository = MongoPDFRepository(database=db)
        document = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="updated content",
            page_count=10,
            file_size=2048,
        )

        result = repository.update(document)

        assert result is not None
        assert result.text_content == "updated content"
        assert result.page_count == 10
        collection.update_one.assert_called_once()

    def test_returns_none_for_nonexistent_document(self, mock_database):
        """Returns None when trying to update non-existent document."""
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)

        repository = MongoPDFRepository(database=db)
        document = PDFDocument(
            id="507f1f77bcf86cd799439011",
            checksum="abc123",
            filename="test.pdf",
            text_content="content",
        )

        result = repository.update(document)

        assert result is None


class TestSoftDelete:
    """Test Soft Delete operation."""

    def test_soft_delete_sets_deleted_at_timestamp(self, mock_database):
        """When deleting, marks deleted_at with current timestamp."""
        db, collection = mock_database

        collection.update_one.return_value = Mock(modified_count=1)

        repository = MongoPDFRepository(database=db)
        result = repository.soft_delete("507f1f77bcf86cd799439011")

        assert result is True
        collection.update_one.assert_called_once()
        # Verifies deleted_at is set
        call_args = collection.update_one.call_args
        assert "$set" in call_args[1]["$set"]
        assert "deleted_at" in call_args[1]["$set"]

    def test_returns_false_for_nonexistent_document(self, mock_database):
        """Returns False when trying to delete non-existent document."""
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)

        repository = MongoPDFRepository(database=db)
        result = repository.soft_delete("507f1f77bcf86cd799439011")

        assert result is False


class TestDeleteById:
    """Test Hard Delete operation."""

    def test_permanently_deletes_document(self, mock_database):
        """Permanently removes document from database."""
        db, collection = mock_database
        collection.delete_one.return_value = Mock(deleted_count=1)

        repository = MongoPDFRepository(database=db)
        result = repository.delete_by_id("507f1f77bcf86cd799439011")

        assert result is True
        collection.delete_one.assert_called_once()

    def test_returns_false_for_nonexistent_document(self, mock_database):
        """Returns False when trying to delete non-existent document."""
        db, collection = mock_database
        collection.delete_one.return_value = Mock(deleted_count=0)

        repository = MongoPDFRepository(database=db)
        result = repository.delete_by_id("507f1f77bcf86cd799439011")

        assert result is False


class TestRestore:
    """Test Restore operation."""

    def test_restores_soft_deleted_document(self, mock_database):
        """Restores document by clearing deleted_at."""
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)

        repository = MongoPDFRepository(database=db)
        result = repository.restore("507f1f77bcf86cd799439011")

        assert result is True
        collection.update_one.assert_called_once()
        # Verify $unset is used to remove deleted_at
        call_args = collection.update_one.call_args
        assert "$unset" in call_args[1]
        assert "deleted_at" in call_args[1]["$unset"]

    def test_returns_false_for_non_deleted_document(self, mock_database):
        """Returns False when trying to restore non-deleted document."""
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)

        repository = MongoPDFRepository(database=db)
        result = repository.restore("507f1f77bcf86cd799439011")

        assert result is False


class TestFilterDeletedDocuments:
    """Test automatic filtering of deleted documents."""

    def test_find_all_excludes_deleted_documents(self, mock_database):
        """Searches by default exclude documents with deleted_at != null."""
        db, collection = mock_database

        collection.find.return_value.sort.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "checksum": "abc123",
                "filename": "active.pdf",
                "text_content": "content",
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        repository = MongoPDFRepository(database=db)
        results = repository.find_all()

        assert len(results) == 1
        collection.find.assert_called_with({"deleted_at": None})

    def test_find_by_id_excludes_deleted(self, mock_database):
        """Finding by ID returns None if document is deleted."""
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_id("507f1f77bcf86cd799439011")

        assert result is None
        collection.find_one.assert_called_with(
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "deleted_at": None,
            }
        )
