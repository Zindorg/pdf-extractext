"""Integration tests for soft delete operation."""

import os
import pytest
from bson import ObjectId
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
