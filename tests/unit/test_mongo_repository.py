"""Tests for MongoPDFRepository."""

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


class TestMongoRepositoryCreate:
    """Tests for create method."""

    def test_create_saves_document_with_generated_id(self, mock_mongo_client):
        """Should save document and return with assigned ID."""
        client, db, collection = mock_mongo_client

        # Mock insert_one to return an ObjectId
        inserted_id = ObjectId("507f1f77bcf86cd799439011")
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        repository = MongoPDFRepository(client, "test_db")
        document = PDFDocument(
            checksum="abc123checksum",
            filename="test.pdf",
            text_content="sample content",
            page_count=1,
            file_size=100
        )

        result = repository.create(document)

        assert result.id == str(inserted_id)
        collection.insert_one.assert_called_once()

    def test_create_preserves_all_fields(self, mock_mongo_client):
        """Should preserve all document fields when saving."""
        client, db, collection = mock_mongo_client
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        repository = MongoPDFRepository(client, "test_db")
        document = PDFDocument(
            checksum="sha256hash",
            filename="document.pdf",
            text_content="full text",
            page_count=5,
            file_size=1024
        )

        result = repository.create(document)

        saved_doc = collection.insert_one.call_args[0][0]
        assert saved_doc["checksum"] == "sha256hash"
        assert saved_doc["filename"] == "document.pdf"
        assert saved_doc["text_content"] == "full text"
        assert saved_doc["page_count"] == 5
        assert saved_doc["file_size"] == 1024


class TestMongoRepositoryFindByChecksum:
    """Tests for find_by_checksum method."""

    def test_find_by_checksum_returns_document_when_found(self, mock_mongo_client):
        """Should return PDFDocument when checksum exists."""
        client, db, collection = mock_mongo_client

        collection.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "checksum": "abc123",
            "filename": "test.pdf",
            "text_content": "content",
            "page_count": 1,
            "file_size": 100,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_checksum("abc123")

        assert result is not None
        assert result.checksum == "abc123"
        assert result.filename == "test.pdf"
        collection.find_one.assert_called_with({"checksum": "abc123"})

    def test_find_by_checksum_returns_none_when_not_found(self, mock_mongo_client):
        """Should return None when checksum not found."""
        client, db, collection = mock_mongo_client
        collection.find_one.return_value = None

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_checksum("nonexistent")

        assert result is None


class TestMongoRepositoryFindById:
    """Tests for find_by_id method."""

    def test_find_by_id_returns_document_when_found(self, mock_mongo_client):
        """Should return PDFDocument when ID exists."""
        client, db, collection = mock_mongo_client

        object_id = ObjectId("507f1f77bcf86cd799439011")
        collection.find_one.return_value = {
            "_id": object_id,
            "checksum": "abc123",
            "filename": "test.pdf",
            "text_content": "content",
            "page_count": 1,
            "file_size": 100,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_id("507f1f77bcf86cd799439011")

        assert result is not None
        assert result.id == "507f1f77bcf86cd799439011"

    def test_find_by_id_returns_none_for_invalid_id(self, mock_mongo_client):
        """Should return None for invalid ObjectId format."""
        client, db, collection = mock_mongo_client

        repository = MongoPDFRepository(client, "test_db")
        result = repository.find_by_id("invalid-id")

        assert result is None


class TestMongoRepositoryFindAll:
    """Tests for find_all method."""

    def test_find_all_returns_list_of_documents(self, mock_mongo_client):
        """Should return list of all documents."""
        client, db, collection = mock_mongo_client

        collection.find.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "checksum": "abc123",
                "filename": "test1.pdf",
                "text_content": "content1",
                "page_count": 1,
                "file_size": 100,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439022"),
                "checksum": "def456",
                "filename": "test2.pdf",
                "text_content": "content2",
                "page_count": 2,
                "file_size": 200,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

        repository = MongoPDFRepository(client, "test_db")
        results = repository.find_all()

        assert len(results) == 2
        assert results[0].filename == "test1.pdf"
        assert results[1].filename == "test2.pdf"

    def test_find_all_returns_empty_list_when_no_documents(self, mock_mongo_client):
        """Should return empty list when collection is empty."""
        client, db, collection = mock_mongo_client
        collection.find.return_value = []

        repository = MongoPDFRepository(client, "test_db")
        results = repository.find_all()

        assert results == []


class TestMongoRepositoryDeleteById:
    """Tests for delete_by_id method."""

    def test_delete_by_id_returns_true_when_deleted(self, mock_mongo_client):
        """Should return True when document is deleted."""
        client, db, collection = mock_mongo_client
        collection.delete_one.return_value = Mock(deleted_count=1)

        repository = MongoPDFRepository(client, "test_db")
        result = repository.delete_by_id("507f1f77bcf86cd799439011")

        assert result is True

    def test_delete_by_id_returns_false_when_not_found(self, mock_mongo_client):
        """Should return False when document not found."""
        client, db, collection = mock_mongo_client
        collection.delete_one.return_value = Mock(deleted_count=0)

        repository = MongoPDFRepository(client, "test_db")
        result = repository.delete_by_id("507f1f77bcf86cd799439011")

        assert result is False

    def test_delete_by_id_returns_false_for_invalid_id(self, mock_mongo_client):
        """Should return False for invalid ObjectId format."""
        client, db, collection = mock_mongo_client

        repository = MongoPDFRepository(client, "test_db")
        result = repository.delete_by_id("invalid-id")

        assert result is False
