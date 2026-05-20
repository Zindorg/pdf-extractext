"""Tests para MongoPDFRepository - crear documento."""

from unittest.mock import Mock

import pytest

from app.exceptions import DuplicateDocumentException
from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_OBJECT_ID, make_mongo_doc, make_pdf_document


class TestCreateDocument:
    """Crear documento guarda metadata y texto."""

    def test_saves_document(self, mock_database):
        db, collection = mock_database
        collection.insert_one.return_value = Mock(inserted_id=SAMPLE_OBJECT_ID)

        repository = MongoPDFRepository(database=db)
        document = make_pdf_document()
        result = repository.create(document)

        assert result.id == str(SAMPLE_OBJECT_ID)
        assert result.checksum == "abc123checksum"
        collection.insert_one.assert_called_once()

    """Crear documento con checksum duplicado lanza exception."""

    def test_raises_duplicate_exception(self, mock_database):
        from pymongo.errors import DuplicateKeyError

        db, collection = mock_database
        collection.insert_one.side_effect = DuplicateKeyError("duplicate key")
        collection.find_one.return_value = make_mongo_doc()

        repository = MongoPDFRepository(database=db)
        document = make_pdf_document(checksum="duplicate_checksum")

        with pytest.raises(DuplicateDocumentException) as exc_info:
            repository.create(document)

        assert exc_info.value.existing_id == str(SAMPLE_OBJECT_ID)
