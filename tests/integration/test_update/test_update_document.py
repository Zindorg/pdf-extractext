"""Integration tests for updating documents."""

import os
import pytest
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
