"""Shared fixtures for integration tests."""

import pytest
from app.infrastructure.database_connection import get_database
from app.repositories.mongo_pdf_repository import MongoPDFRepository


@pytest.fixture(scope="module")
def mongo_repository():
    """Provide MongoDB repository connected to test database.

    Nota: Requiere MongoDB corriendo en localhost:27017
    """
    try:
        db = get_database()
        repository = MongoPDFRepository(database=db)

        # Clean up any existing test data
        db["pdf_documents"].delete_many({"filename": {"$regex": "^test_"}})

        yield repository

        # Cleanup after tests
        db["pdf_documents"].delete_many({"filename": {"$regex": "^test_"}})
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")
