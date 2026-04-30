"""Integration tests for restoring documents."""

import os
import pytest
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


class TestRestore:
    """Test RESTORE operation."""

    def test_restore_recovers_soft_deleted_document(self, mongo_repository):
        """Verify restore recovers soft-deleted document."""
        doc = PDFDocument(
            checksum="test_restore",
            filename="test_restore.pdf",
            text_content="To be restored",
        )
        created = mongo_repository.create(doc)
        mongo_repository.soft_delete(created.id)

        # Verify deleted
        assert mongo_repository.find_by_id(created.id) is None

        # Restore
        result = mongo_repository.restore(created.id)
        assert result is True

        # Should be findable again
        restored = mongo_repository.find_by_id(created.id)
        assert restored is not None
        assert restored.checksum == "test_restore"

    def test_restore_returns_false_for_non_deleted_document(self, mongo_repository):
        """Verify restoring non-deleted document returns False."""
        doc = PDFDocument(
            checksum="test_restore_active",
            filename="test_restore_active.pdf",
            text_content="Active document",
        )
        created = mongo_repository.create(doc)

        result = mongo_repository.restore(created.id)
        assert result is False
