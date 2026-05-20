"""Tests para MongoPDFRepository - buscar por ID."""

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_OBJECT_ID, make_mongo_doc


class TestFindById:
    """Buscar por ID retorna documento."""

    def test_returns_document(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = make_mongo_doc()

        repository = MongoPDFRepository(database=db)
        result = repository.find_by_id(str(SAMPLE_OBJECT_ID))

        assert result is not None
        assert result.id == str(SAMPLE_OBJECT_ID)

    """Buscar por ID invalido retorna None."""

    def test_returns_none(self, mock_database):
        db, _ = mock_database
        repository = MongoPDFRepository(database=db)
        assert repository.find_by_id("invalid-non-mongo-id") is None

    """Buscar por ID eliminado retorna None."""

    def test_returns_none(self, mock_database):
        db, collection = mock_database
        collection.find_one.return_value = None

        repository = MongoPDFRepository(database=db)
        assert repository.find_by_id(str(SAMPLE_OBJECT_ID)) is None
