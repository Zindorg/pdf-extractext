"""Tests para propiedad is_connected."""

from unittest.mock import patch

from app.infrastructure.database_connection import DatabaseConnection
from tests.unit.infrastructure.database_connection._mock_mongo_client import _mock_mongo_client

class TestIsConnectedProperty:
    """Propiedad is_connected refleja estado."""

    def test_reflects_state(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            _mock_mongo_client(mock_client)
            connection = DatabaseConnection()
            assert connection.is_connected is False
            connection.connect()
            assert connection.is_connected is True
            connection.close()
            assert connection.is_connected is False
