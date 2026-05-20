import os
import pytest
import uuid
from datetime import datetime
from bson import ObjectId
from app.models.pdf_document import PDFDocument
from app.exceptions import DuplicateDocumentException

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS") == "1",
    reason="Integration tests disabled"
)

@pytest.fixture(autouse=True)
def clean_collection(mongo_repository):
    mongo_repository._collection.delete_many({})
    yield
    mongo_repository._collection.delete_many({})

class TestCreateDocument:
    """Test CREATE operation."""

    def test_create_persists_document_to_database(self, mongo_repository):
        document = PDFDocument(
            checksum=f"test_create_{uuid.uuid4().hex}",
            filename="test_create.pdf",
            text_content="Integration test content",
            page_count=5,
            file_size=1024,
        )
        result = mongo_repository.create(document)
        assert result.id is not None
        raw_doc = mongo_repository._collection.find_one({"_id": ObjectId(result.id)})
        assert raw_doc["checksum"] == document.checksum

    def test_create_generates_timestamps(self, mongo_repository):
        document = PDFDocument(
            checksum=f"test_timestamps_{uuid.uuid4().hex}",
            filename="test_timestamps.pdf",
            text_content="Test content",
        )
        result = mongo_repository.create(document)
        raw_doc = mongo_repository._collection.find_one({"_id": ObjectId(result.id)})
        assert isinstance(raw_doc["created_at"], datetime)
        assert raw_doc["updated_at"] is not None

    def test_create_raises_duplicate_exception_on_checksum_collision(self, mongo_repository):
        checksum = f"test_duplicate_{uuid.uuid4().hex}"
        doc1 = PDFDocument(checksum=checksum, filename="dup1.pdf", text_content="First")
        mongo_repository.create(doc1)
        doc2 = PDFDocument(checksum=checksum, filename="dup2.pdf", text_content="Second")
        with pytest.raises(DuplicateDocumentException):
            mongo_repository.create(doc2)
