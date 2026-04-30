"""Integration tests for hard delete operation."""

import os
import pytest
from bson import ObjectId
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
