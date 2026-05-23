"""Fixtures exclusivas para tests unitarios."""

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from bson import ObjectId
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


@pytest.fixture
def mock_database():
    """Crea un mock de MongoDB (db, collection) listo para usar."""
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__ = Mock(return_value=collection)
    db.pdf_documents = collection
    return db, collection
