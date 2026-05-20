"""Tests para MongoPDFRepository - actualizar documento."""

from unittest.mock import Mock

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import make_mongo_doc, make_pdf_document


class TestUpdateUpdatesFields:
    """Actualizar modifica campos del documento."""

    def test_updates_fields(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)
        collection.find_one.return_value = make_mongo_doc(text_content="updated content")

        repository = MongoPDFRepository(database=db)
        result = repository.update(make_pdf_document(text_content="updated content"))

        assert result is not None
        assert result.text_content == "updated content"

    """Actualizar documento inexistente retorna None."""

    def test_returns_none(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)

        repository = MongoPDFRepository(database=db)
        assert repository.update(make_pdf_document()) is None
