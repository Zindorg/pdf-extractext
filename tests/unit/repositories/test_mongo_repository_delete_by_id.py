"""Tests para MongoPDFRepository - eliminar permanentemente."""

from unittest.mock import Mock

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_OBJECT_ID


class TestDeleteByIdDeletesDocument:
    """Eliminar permanentemente documento existente."""

    def test_returns_true(self, mock_database):
        db, collection = mock_database
        collection.delete_one.return_value = Mock(deleted_count=1)
        repository = MongoPDFRepository(database=db)
        assert repository.delete_by_id(str(SAMPLE_OBJECT_ID)) is True

    """Eliminar permanentemente documento inexistente retorna False."""

    def test_returns_false(self, mock_database):
        db, collection = mock_database
        collection.delete_one.return_value = Mock(deleted_count=0)
        repository = MongoPDFRepository(database=db)
        assert repository.delete_by_id(str(SAMPLE_OBJECT_ID)) is False
