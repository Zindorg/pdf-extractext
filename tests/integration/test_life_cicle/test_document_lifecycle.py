"""Integration tests for complete document lifecycle."""


from app.models.pdf_document import PDFDocument

from tests.integration.test_creation_document.test_create_document import pytestmark

class TestDocumentLifecycle:
    """Test complete CRUD lifecycle."""

    def _create_sample_doc(self, checksum="test_doc", text="Initial content", pages=5):
        """Factory interna para evitar repetición (DRY)."""
        return PDFDocument(
            checksum=checksum,
            filename=f"{checksum}.pdf",
            text_content=text,
            page_count=pages,
        )

    def test_create_document_assigns_id(self, mongo_repository):
        doc = self._create_sample_doc(checksum="create_test")
        created = mongo_repository.create(doc)
        assert created.id is not None

    def test_read_document_returns_content(self, mongo_repository):
        doc = self._create_sample_doc(checksum="read_test", text="Read me")
        created = mongo_repository.create(doc)
        found = mongo_repository.find_by_id(created.id)
        assert found is not None
        assert found.text_content == "Read me"

    def test_hard_delete_document_removes_permanently(self, mongo_repository):
        doc = self._create_sample_doc(checksum="hard_delete_test")
        created = mongo_repository.create(doc)
        assert mongo_repository.delete_by_id(created.id) is True
        assert mongo_repository.find_by_id(created.id) is None