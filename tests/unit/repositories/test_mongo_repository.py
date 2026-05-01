"""Tests para MongoPDFRepository."""

from unittest.mock import Mock

import pytest
from bson import ObjectId

from app.exceptions import DuplicateDocumentException
from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_CHECKSUM, SAMPLE_OBJECT_ID, make_mongo_doc, make_pdf_document


class TestCreateDocument:
    def test_saves_document_with_metadata_and_text(self, mock_database):
        db, collection = mock_database
        collection.insert_one.return_value = Mock(inserted_id=SAMPLE_OBJECT_ID)

        repository = MongoPDFRepository(database=db)
        document = make_pdf_document()
        result = repository.create(document)

        assert result.id == str(SAMPLE_OBJECT_ID)
        assert result.checksum == "abc123checksum"
        collection.insert_one.assert_called_once()

    def test_raises_duplicate_exception_on_checksum_collision(self, mock_database):
        from pymongo.errors import DuplicateKeyError

        db, collection = mock_database
        collection.insert_one.side_effect = DuplicateKeyError("duplicate key")
        collection.find_one.return_value = make_mongo_doc()

        repository = MongoPDFRepository(database=db)
        document = make_pdf_document(checksum="duplicate_checksum")

        with pytest.raises(DuplicateDocumentException) as exc_info:
            repository.create(document)

        assert exc_info.value.existing_id == str(SAMPLE_OBJECT_ID)


class TestFindByChecksum:
    def test_finds_document_by_checksum(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = make_mongo_doc()

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_checksum("abc123")

        assert result is not None
        assert result.checksum == SAMPLE_CHECKSUM
        collection.find_one.assert_called_with({"checksum": "abc123", "deleted_at": None})

    def test_returns_none_for_nonexistent_checksum(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        assert repository.find_by_checksum("nonexistent") is None


class TestFindById:
    def test_gets_document_by_id(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = make_mongo_doc()

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_id(str(SAMPLE_OBJECT_ID))

        assert result is not None
        assert result.id == str(SAMPLE_OBJECT_ID)

    def test_returns_none_for_invalid_id_format(self, mock_database):
        db, _ = mock_database
        repository = MongoPDFRepository(database=db)
        assert repository.find_by_id("invalid-non-mongo-id") is None

    def test_returns_none_for_deleted_document(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        assert repository.find_by_id(str(SAMPLE_OBJECT_ID)) is None


class TestFindAll:
    def test_returns_list_of_active_documents(self, mock_database):
        db, collection = mock_database
        collection.find.return_value.sort.return_value = [
            make_mongo_doc(filename="doc1.pdf"),
            make_mongo_doc(_id=ObjectId("507f1f77bcf86cd799439012"), filename="doc2.pdf"),
        ]

        repository = MongoPDFRepository(database=db)
        results = repository.find_all()

        assert len(results) == 2
        collection.find.assert_called_with({"deleted_at": None})

    def test_returns_empty_list_when_no_documents(self, mock_database):
        db, collection = mock_database
        collection.find.return_value.sort.return_value = []

        repository = MongoPDFRepository(database=db)
        assert repository.find_all() == []


class TestUpdateDocument:
    def test_updates_document_fields(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)
        collection.find_one.return_value = make_mongo_doc(text_content="updated content")

        repository = MongoPDFRepository(database=db)
        result = repository.update(make_pdf_document(text_content="updated content"))

        assert result is not None
        assert result.text_content == "updated content"
        collection.update_one.assert_called_once()

    def test_returns_none_for_nonexistent_document(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)

        repository = MongoPDFRepository(database=db)
        assert repository.update(make_pdf_document()) is None


class TestSoftDelete:
    def test_returns_true_when_document_exists(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)
        repository = MongoPDFRepository(database=db)
        assert repository.soft_delete(str(SAMPLE_OBJECT_ID)) is True

    def test_returns_false_for_nonexistent_document(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)
        repository = MongoPDFRepository(database=db)
        assert repository.soft_delete(str(SAMPLE_OBJECT_ID)) is False


class TestDeleteById:
    def test_permanently_deletes_document(self, mock_database):
        db, collection = mock_database
        collection.delete_one.return_value = Mock(deleted_count=1)
        repository = MongoPDFRepository(database=db)
        assert repository.delete_by_id(str(SAMPLE_OBJECT_ID)) is True
        collection.delete_one.assert_called_once()

    def test_returns_false_for_nonexistent_document(self, mock_database):
        db, collection = mock_database
        collection.delete_one.return_value = Mock(deleted_count=0)
        repository = MongoPDFRepository(database=db)
        assert repository.delete_by_id(str(SAMPLE_OBJECT_ID)) is False


class TestRestore:
    def test_restores_soft_deleted_document(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)
        repository = MongoPDFRepository(database=db)
        assert repository.restore(str(SAMPLE_OBJECT_ID)) is True

    def test_returns_false_for_non_deleted_document(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)
        repository = MongoPDFRepository(database=db)
        assert repository.restore(str(SAMPLE_OBJECT_ID)) is False
