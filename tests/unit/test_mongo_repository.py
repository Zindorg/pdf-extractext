"""Tests for MongoPDFRepository - 5 essential behavior tests."""

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from bson import ObjectId

from models.pdf_document import PDFDocument
from repositories.mongo_pdf_repository import MongoPDFRepository


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client."""
    client = MagicMock()
    db = MagicMock()
    collection = MagicMock()

    client.__getitem__ = Mock(return_value=db)
    db.__getitem__ = Mock(return_value=collection)
    db.pdf_documents = collection

    return client, db, collection


class TestCreateDocument:
    """Test 1: Successful save of metadata and text."""

    def test_saves_document_with_metadata_and_text(self, mock_mongo_client):
        """Saves PDF document and returns with MongoDB generated ID."""
        client, db, collection = mock_mongo_client

        inserted_id = ObjectId("507f1f77bcf86cd799439011")
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        repository = MongoPDFRepository(client, "test_db")
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


class TestFindByChecksum:
    """Test 2: Duplicate validation through checksum."""

    def test_finds_document_by_checksum(self, mock_mongo_client):
        """Finds existing document by its unique checksum."""
        client, db, collection = mock_mongo_client

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

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_checksum("abc123")

        assert result is not None
        assert result.checksum == "abc123"
        # Verifies it excludes deleted by default
        collection.find_one.assert_called_with(
            {"checksum": "abc123", "deleted_at": None}
        )


class TestSoftDelete:
    """Test 3: Soft delete functionality."""

    def test_soft_delete_sets_deleted_at_timestamp(self, mock_mongo_client):
        """When deleting, marks deleted_at with current timestamp."""
        client, db, collection = mock_mongo_client

        collection.update_one.return_value = Mock(modified_count=1)

        repository = MongoPDFRepository(client, "test_db")
        result = repository.soft_delete("507f1f77bcf86cd799439011")

        assert result is True
        collection.update_one.assert_called_once()
        # Verifies deleted_at is set
        call_args = collection.update_one.call_args
        assert "$set" in call_args[0][1]
        assert "deleted_at" in call_args[0][1]["$set"]


class TestFilterDeletedDocuments:
    """Test 4: Automatic filtering of deleted documents."""

    def test_search_excludes_deleted_documents(self, mock_mongo_client):
        """Searches by default exclude documents with deleted_at != null."""
        client, db, collection = mock_mongo_client

        collection.find.return_value = [
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

        repository = MongoPDFRepository(client, "test_db")
        results = repository.find_all()

        assert len(results) == 1
        # Verifies filter excludes deleted
        collection.find.assert_called_with({"deleted_at": None})

    def test_find_by_id_excludes_deleted(self, mock_mongo_client):
        """Finding by ID returns None if document is deleted."""
        client, db, collection = mock_mongo_client

        # Simulates not found (deleted)
        collection.find_one.return_value = None

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_id("507f1f77bcf86cd799439011")

        assert result is None
        collection.find_one.assert_called_with(
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "deleted_at": None,
            }
        )


class TestGetDocumentById:
    """Test 5: Get document by ID."""

    def test_gets_document_by_id(self, mock_mongo_client):
        """Returns document when searching by valid ID."""
        client, db, collection = mock_mongo_client

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

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_id("507f1f77bcf86cd799439011")

        assert result is not None
        assert result.id == "507f1f77bcf86cd799439011"
        assert result.filename == "test.pdf"

    def test_returns_none_for_invalid_id_format(self, mock_mongo_client):
        """Returns None for invalid MongoDB ID format."""
        client, db, collection = mock_mongo_client

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_id("invalid-non-mongo-id")

        assert result is None
