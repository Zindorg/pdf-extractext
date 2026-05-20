"""Tests para MongoPDFRepository - restaurar documento."""

from unittest.mock import Mock

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_OBJECT_ID


class TestRestoreRestoresSoftDeleted:
    """Restaurar documento eliminado logicamente."""

    def test_returns_true(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)
        repository = MongoPDFRepository(database=db)
        assert repository.restore(str(SAMPLE_OBJECT_ID)) is True

    """Restaurar documento no eliminado retorna False."""

    def test_returns_false(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)
        repository = MongoPDFRepository(database=db)
        assert repository.restore(str(SAMPLE_OBJECT_ID)) is False
