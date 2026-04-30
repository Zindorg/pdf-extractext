"""Integration tests for finding documents by ID."""

import os
import pytest
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
