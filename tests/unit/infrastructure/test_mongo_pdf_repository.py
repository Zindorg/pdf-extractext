"""Comportamiento propio del adaptador MongoDB (más allá del contrato)."""

from unittest.mock import MagicMock

import mongomock
import pytest
from pymongo.errors import PyMongoError

from app.domain.exceptions import DuplicateDocumentException, RepositoryException
from app.infrastructure.database_setup import setup_database
from app.infrastructure.mongo_pdf_repository import MongoPDFRepository
from tests.unit.factories import make_pdf_document


def test_unique_index_rejects_duplicate_checksums():
    """El índice único es la única fuente de verdad de la deduplicación."""
    repo = MongoPDFRepository(setup_database(mongomock.MongoClient().db))
    repo.create(make_pdf_document(checksum="race"))

    with pytest.raises(DuplicateDocumentException):
        repo.create(make_pdf_document(checksum="race"))


@pytest.mark.parametrize(
    "call",
    [
        lambda repo: repo.create(make_pdf_document()),
        lambda repo: repo.find_by_id("507f1f77bcf86cd799439011"),
        lambda repo: repo.find_all(),
        lambda repo: repo.delete_by_id("507f1f77bcf86cd799439011"),
    ],
    ids=["create", "find_by_id", "find_all", "delete_by_id"],
)
def test_database_errors_surface_as_repository_exception(call):
    """Una caída de MongoDB nunca debe parecer un 'no encontrado'."""
    collection = MagicMock()
    for method in ("insert_one", "find_one", "find", "delete_one"):
        getattr(collection, method).side_effect = PyMongoError("connection refused")
    database = MagicMock()
    database.__getitem__.return_value = collection

    with pytest.raises(RepositoryException):
        call(MongoPDFRepository(database))
