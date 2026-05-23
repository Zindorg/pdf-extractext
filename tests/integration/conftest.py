"""Shared fixtures for integration tests."""

from pymongo import MongoClient
import pytest

from app.config.settings import settings
from app.infrastructure.database_setup import create_indexes
from app.repositories.mongo_pdf_repository import MongoPDFRepository


@pytest.fixture(scope="module")
def mongo_repository():
    """Provide MongoDB repository connected to test database.

    Nota: Requiere MongoDB corriendo en localhost:27017
    """
    try:
        client = MongoClient(settings.mongodb_uri)
        db = client[settings.mongodb_database]
        create_indexes(db)
        repository = MongoPDFRepository(database=db)

        # Clean up any existing test data
        db["pdf_documents"].delete_many({"filename": {"$regex": "^test_"}})

        yield repository

        # Cleanup after tests
        db["pdf_documents"].delete_many({"filename": {"$regex": "^test_"}})
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")