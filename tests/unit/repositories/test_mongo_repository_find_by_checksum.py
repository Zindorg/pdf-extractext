"""Tests para MongoPDFRepository - buscar por checksum."""

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_CHECKSUM, make_mongo_doc


class TestFindByChecksum:
    """Buscar por checksum retorna documento."""

    def test_finds_document(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = make_mongo_doc()

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_checksum("abc123")

        assert result is not None
        assert result.checksum == SAMPLE_CHECKSUM

    """Buscar por checksum inexistente retorna None."""

    def test_returns_none(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        assert repository.find_by_checksum("nonexistent") is None
