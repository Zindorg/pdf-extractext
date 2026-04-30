"""Integration tests for finding documents by checksum."""

import os
import pytest
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
