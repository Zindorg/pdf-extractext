"""Integration tests for finding all documents."""

import os
import pytest
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


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
