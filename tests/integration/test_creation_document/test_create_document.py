"""Integration tests for document creation."""

import os
import pytest
from datetime import datetime
from bson import ObjectId
from app.models.pdf_document import PDFDocument
from app.exceptions import DuplicateDocumentException

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
