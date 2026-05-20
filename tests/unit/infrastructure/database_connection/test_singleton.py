"""Tests para singleton de DatabaseConnection."""

from unittest.mock import patch

from app.infrastructure.database_connection import DatabaseConnection
from tests.unit.infrastructure.database_connection._mock_mongo_client import _mock_mongo_client


class TestSingletonReturnsSameInstance:
    """Singleton retorna misma instancia."""

    def test_returns_same_instance(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            _mock_mongo_client(mock_client)
            db1 = DatabaseConnection().connect()
            db2 = DatabaseConnection().connect()
            assert db1 is db2
