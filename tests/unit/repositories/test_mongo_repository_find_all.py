"""Tests para MongoPDFRepository - buscar todos."""

from bson import ObjectId

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import make_mongo_doc


class TestFindAllReturnsList:
    """Buscar todos retorna lista de documentos."""

    def test_returns_list(self, mock_database):
        db, collection = mock_database
        collection.find.return_value.sort.return_value = [
            make_mongo_doc(filename="doc1.pdf"),
            make_mongo_doc(_id=ObjectId("507f1f77bcf86cd799439012"), filename="doc2.pdf"),
        ]

        repository = MongoPDFRepository(database=db)
        results = repository.find_all()

        assert len(results) == 2

    """Buscar todos sin documentos retorna lista vacia."""

    def test_returns_empty_list(self, mock_database):
        db, collection = mock_database
        collection.find.return_value.sort.return_value = []

        repository = MongoPDFRepository(database=db)
        assert repository.find_all() == []
