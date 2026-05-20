"""Tests para MongoPDFRepository - soft delete."""

from unittest.mock import Mock

from app.repositories.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import SAMPLE_OBJECT_ID


class TestSoftDelete:
    """Soft delete de documento existente retorna True."""

    def test_returns_true(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=1)
        repository = MongoPDFRepository(database=db)
        assert repository.soft_delete(str(SAMPLE_OBJECT_ID)) is True

    """Soft delete de documento inexistente retorna False."""

    def test_returns_false(self, mock_database):
        db, collection = mock_database
        collection.update_one.return_value = Mock(modified_count=0)
        repository = MongoPDFRepository(database=db)
        assert repository.soft_delete(str(SAMPLE_OBJECT_ID)) is False
