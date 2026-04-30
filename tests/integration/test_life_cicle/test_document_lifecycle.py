"""Integration tests for complete document lifecycle."""

import os
import pytest
from app.models.pdf_document import PDFDocument

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)


class TestDocumentLifecycle:
    """Test complete CRUD lifecycle."""

    def test_full_create_read_update_delete_cycle(self, mongo_repository):
        """Verify complete document lifecycle."""
        # CREATE
        doc = PDFDocument(
            checksum="test_lifecycle",
            filename="test_lifecycle.pdf",
            text_content="Initial content",
            page_count=5,
        )
        created = mongo_repository.create(doc)
        assert created.id is not None

        # READ
        found = mongo_repository.find_by_id(created.id)
        assert found.text_content == "Initial content"

        # UPDATE
        found.text_content = "Updated content"
        updated = mongo_repository.update(found)
        assert updated.text_content == "Updated content"

        # SOFT DELETE
        assert mongo_repository.soft_delete(created.id) is True
        assert mongo_repository.find_by_id(created.id) is None

        # RESTORE
        assert mongo_repository.restore(created.id) is True
        restored = mongo_repository.find_by_id(created.id)
        assert restored is not None

        # HARD DELETE
        assert mongo_repository.delete_by_id(created.id) is True
        assert mongo_repository.find_by_id(created.id) is None
