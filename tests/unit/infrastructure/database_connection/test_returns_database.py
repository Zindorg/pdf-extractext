"""Tests para retorno de base de datos."""

from unittest.mock import patch

from app.infrastructure.database_connection import DatabaseConnection
from tests.unit.infrastructure.database_connection._mock_mongo_client import _mock_mongo_client

class TestReturnsDatabaseWithConfiguredName:
    """Retorna base de datos con nombre configurado."""

    def test_returns_configured_database(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            _, mock_db = _mock_mongo_client(mock_client)
            db = DatabaseConnection().connect()
            assert db is mock_db
