"""Integration tests for finding all documents."""

from app.models.pdf_document import PDFDocument
from tests.integration.test_creation_document.test_create_document import pytestmark

class TestFindAll:
    """Test READ all operation."""

    def test_find_all_returns_list_of_documents(self, mongo_repository):
        """Verify find_all returns all documents."""
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
